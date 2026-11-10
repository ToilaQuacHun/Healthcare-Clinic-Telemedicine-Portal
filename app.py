"""MediConnect Phase 4: server-rendered Flask app for the original Phrase3 schema.

Educational demonstration with synthetic data only. No REST API.
"""
import hmac
import logging
import os
import secrets
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from mysql.connector import Error, IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection

load_dotenv()
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', '0') == '1',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
)
logging.basicConfig(level=logging.INFO)


class InvalidInput(Exception):
    pass


def rows(sql, params=()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def one(sql, params=()):
    result = rows(sql, params)
    return result[0] if result else None


@contextmanager
def write_tx():
    """Serialize app-side mutations for non-AUTO_INCREMENT PKs and rechecks.

    This does NOT prevent changes made by OTHER apps bypassing these routes.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    locked = False
    try:
        cur.execute("SELECT GET_LOCK('MC_PHASE4_WRITE', 10) AS acquired")
        locked = bool(cur.fetchone()['acquired'])
        if not locked:
            raise InvalidInput('Hệ thống đang bận. Hãy thử lại.')
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if locked:
            try:
                cur.execute("SELECT RELEASE_LOCK('MC_PHASE4_WRITE')")
                cur.fetchone()
            except Error:
                pass
        cur.close()
        conn.close()


IDS = {
    'USER_ACCOUNT': 'UserID', 'PATIENT': 'Patient', 'DOCTOR': 'DoctorID',
    'DOCTOR_SCHEDULE': 'ScheduleID', 'APPOINTMENT': 'AppointmentID',
    'CONSULTATION_SESSION': 'SessionID', 'PRESCRIPTION': 'PrescriptionID',
    'PRESCRIPTION_ITEM': 'PrescriptionItemID',
}


def next_id(cur, table):
    if table not in IDS:
        raise ValueError('Unsupported ID table')
    cur.execute(f'SELECT COALESCE(MAX({IDS[table]}), 0) + 1 AS next_id FROM {table}')
    return int(cur.fetchone()['next_id'])


def cur_one(cur, sql, args=()):
    cur.execute(sql, args)
    return cur.fetchone()


def required(field, label, limit=255):
    value = request.form.get(field, '').strip()
    if not value or len(value) > limit:
        raise InvalidInput(f'{label} bắt buộc và không quá {limit} ký tự.')
    return value


def number(field, label, minimum=1):
    try:
        n = int(request.form.get(field, ''))
    except (TypeError, ValueError):
        raise InvalidInput(f'{label} phải là số nguyên.')
    if n < minimum:
        raise InvalidInput(f'{label} không hợp lệ.')
    return n


def safe_action(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidInput as exc:
            flash(str(exc), 'warning')
        except IntegrityError:
            app.logger.exception('Integrity rule blocked request')
            flash('Thao tác bị từ chối bởi khóa ngoại, UNIQUE hoặc ràng buộc.', 'danger')
        except Error as exc:
            app.logger.exception('MySQL error')
            if getattr(exc, 'errno', None) == 1644:
                flash('Trigger MySQL từ chối: ' + str(exc.msg), 'danger')
            else:
                flash('Lỗi MySQL. Xem Terminal của Flask để biết chi tiết.', 'danger')
        return redirect(request.form.get('_return') or url_for('dashboard'))
    return wrapped


def csrf_token():
    if '_csrf' not in session:
        session['_csrf'] = secrets.token_urlsafe(32)
    return session['_csrf']


@app.context_processor
def context_vars():
    return {'csrf_token': csrf_token, 'current_year': date.today().year}


@app.before_request
def auth_guard():
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        token = request.form.get('_csrf', '')
        if not hmac.compare_digest(str(session.get('_csrf', '')), str(token)) or not token:
            abort(400, 'CSRF token không hợp lệ. Tải lại trang và thử lại.')

    if request.endpoint in ('login', 'static'):
        return
    if not session.get('user_id'):
        return redirect(url_for('login'))

    # Session cannot grant access to a deleted/unlinked profile.
    role = session.get('role')
    profile_id = session.get('profile_id')
    if role in ('DOCTOR', 'PATIENT') and not profile_id:
        session.clear()
        return redirect(url_for('login'))
    if role == 'DOCTOR' and not one(
        'SELECT DoctorID FROM DOCTOR WHERE DoctorID=%s AND UserID=%s AND IsActive=1',
        (profile_id, session['user_id'])):
        session.clear()
        return redirect(url_for('login'))
    if role == 'PATIENT' and not one(
        'SELECT Patient FROM PATIENT WHERE Patient=%s AND UserID=%s',
        (profile_id, session['user_id'])):
        session.clear()
        return redirect(url_for('login'))


def allow(*roles):
    def decorate(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if session.get('role') not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorate


@app.after_request
def security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Cache-Control'] = 'no-store'
    return response


def verified_password(saved, supplied):
    saved = str(saved or '')
    if saved.startswith(('scrypt:', 'pbkdf2:')):
        return check_password_hash(saved, supplied), False
    if saved.startswith(('DEMO_DISABLED_', 'DEMO_DISABLED_SHA256:')):
        return False, False
    # Compatibility with the ORIGINAL Phase3 sample file's plaintext values.
    # Immediately upgrade on login; never use this path for real patient data.
    return bool(saved) and hmac.compare_digest(saved, supplied), True


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            user = one('SELECT UserID,Username,PasswordHash,Role FROM USER_ACCOUNT WHERE Username=%s', (username,))
            if user:
                valid, legacy = verified_password(user['PasswordHash'], password)
                if valid:
                    role = user['Role']
                    profile = None
                    if role == 'DOCTOR':
                        profile = one('SELECT DoctorID AS id FROM DOCTOR WHERE UserID=%s AND IsActive=1', (user['UserID'],))
                    elif role == 'PATIENT':
                        profile = one('SELECT Patient AS id FROM PATIENT WHERE UserID=%s', (user['UserID'],))
                    if role == 'ADMIN' or (role in ('PATIENT', 'DOCTOR') and profile):
                        if legacy:
                            with write_tx() as cur:
                                cur.execute('UPDATE USER_ACCOUNT SET PasswordHash=%s WHERE UserID=%s',
                                            (generate_password_hash(password), user['UserID']))
                        session.clear()
                        session.permanent = True
                        session.update(user_id=user['UserID'], username=user['Username'],
                                       role=role, profile_id=profile['id'] if profile else None)
                        flash('Đăng nhập thành công.', 'success')
                        return redirect(url_for('dashboard' if role == 'ADMIN' else 'appointments'))
            flash('Sai tài khoản/mật khẩu hoặc hồ sơ chưa được kích hoạt.', 'danger')
        except Error:
            app.logger.exception('Login database error')
            flash('Không thể kết nối database. Kiểm tra cấu hình và migration.', 'danger')
    return render_template('login.html')


@app.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


def page_info(total, default=20):
    try:
        per = int(request.args.get('per_page', default))
        page = int(request.args.get('page', 1))
    except ValueError:
        per, page = default, 1
    if per not in (10, 20, 50, 100):
        per = default
    pages = max(1, (int(total) + per - 1) // per)
    page = max(1, min(page, pages))
    return {'page': page, 'per_page': per, 'total': int(total), 'pages': pages,
            'offset': (page - 1) * per, 'window': range(max(1, page - 2), min(pages, page + 2) + 1)}


@app.route('/')
def dashboard():
    if session['role'] != 'ADMIN':
        return redirect(url_for('appointments'))
    counts = one('''SELECT (SELECT COUNT(*) FROM PATIENT) patients,
        (SELECT COUNT(*) FROM DOCTOR WHERE IsActive=1) doctors,
        (SELECT COUNT(*) FROM APPOINTMENT) appointments,
        (SELECT COUNT(*) FROM PRESCRIPTION) prescriptions''')
    latest = rows('''SELECT AppointmentID,PatientName,DoctorName,AppointmentDateTime,Modality,Status
                     FROM vw_AppointmentDetails ORDER BY AppointmentDateTime DESC LIMIT 8''')
    return render_template('dashboard.html', counts=counts, latest=latest)


@app.route('/patients')
@allow('ADMIN')
def patients():
    q = request.args.get('q', '').strip()[:100]
    where, args = (' WHERE FullName LIKE %s', (f'%{q}%',)) if q else ('', ())
    total = one('SELECT COUNT(*) total FROM PATIENT' + where, args)['total']
    pg = page_info(total)
    data = rows('SELECT Patient,UserID,FullName,BloodType,EmergencyContact FROM PATIENT'
                + where + ' ORDER BY Patient DESC LIMIT %s OFFSET %s', args + (pg['per_page'], pg['offset']))
    return render_template('patients.html', rows=data, pg=pg, q=q)


@app.post('/patients/new')
@allow('ADMIN')
@safe_action
def patient_create():
    name = required('full_name', 'Tên bệnh nhân', 100)
    username = required('username', 'Username', 50)
    password = required('password', 'Mật khẩu', 100)
    if len(password) < 8:
        raise InvalidInput('Mật khẩu cần tối thiểu 8 ký tự.')
    blood = request.form.get('blood_type', '').strip()[:5] or None
    emergency = request.form.get('emergency_contact', '').strip()[:20] or None
    allergies = request.form.get('allergies', '').strip() or None
    chronic = request.form.get('chronic_diseases', '').strip() or None
    with write_tx() as cur:
        user_id = next_id(cur, 'USER_ACCOUNT')
        patient_id = next_id(cur, 'PATIENT')
        cur.execute('INSERT INTO USER_ACCOUNT (UserID,Username,PasswordHash,Role) VALUES (%s,%s,%s,%s)',
                    (user_id, username, generate_password_hash(password), 'PATIENT'))
        cur.execute('''INSERT INTO PATIENT (Patient,UserID,FullName,BloodType,Allergies,ChronicDiseases,EmergencyContact)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                    (patient_id, user_id, name, blood, allergies, chronic, emergency))
    flash(f'Đã thêm bệnh nhân #{patient_id}.', 'success')
    return redirect(url_for('patients'))


@app.post('/patients/<int:patient_id>/edit')
@allow('ADMIN')
@safe_action
def patient_edit(patient_id):
    name = required('full_name', 'Tên bệnh nhân', 100)
    with write_tx() as cur:
        cur.execute('''UPDATE PATIENT SET FullName=%s,BloodType=%s,EmergencyContact=%s
                       WHERE Patient=%s''',
                    (name, request.form.get('blood_type') or None,
                     request.form.get('emergency_contact') or None, patient_id))
        if not cur.rowcount:
            raise InvalidInput('Không tìm thấy bệnh nhân.')
    flash('Đã cập nhật bệnh nhân.', 'success')
    return redirect(url_for('patients'))


@app.post('/patients/<int:patient_id>/delete')
@allow('ADMIN')
@safe_action
def patient_delete(patient_id):
    with write_tx() as cur:
        patient = cur_one(cur, 'SELECT Patient,UserID FROM PATIENT WHERE Patient=%s FOR UPDATE', (patient_id,))
        if not patient:
            raise InvalidInput('Không tìm thấy bệnh nhân.')
        blocked = cur_one(cur, '''SELECT
            (SELECT COUNT(*) FROM APPOINTMENT WHERE Patient=%s) a,
            (SELECT COUNT(*) FROM PRESCRIPTION WHERE Patient=%s) p,
            (SELECT COUNT(*) FROM MEDICAL_HISTORY WHERE Patient=%s) h''', (patient_id, patient_id, patient_id))
        if any(blocked.values()):
            raise InvalidInput('Không thể xóa bệnh nhân đã có lịch hẹn, đơn thuốc hoặc bệnh án.')
        cur.execute('DELETE FROM PATIENT WHERE Patient=%s', (patient_id,))
        if patient['UserID']:
            cur.execute("DELETE FROM USER_ACCOUNT WHERE UserID=%s AND Role='PATIENT'", (patient['UserID'],))
    flash('Đã xóa bệnh nhân chưa phát sinh dữ liệu khám.', 'success')
    return redirect(url_for('patients'))


@app.route('/doctors')
@allow('ADMIN')
def doctors():
    q = request.args.get('q', '').strip()[:100]
    where, args = (' WHERE d.FullName LIKE %s', (f'%{q}%',)) if q else ('', ())
    total = one('SELECT COUNT(*) total FROM DOCTOR d' + where, args)['total']
    pg = page_info(total)
    data = rows('''SELECT d.DoctorID,d.FullName,d.ContactInfo,d.LicenseNumber,d.IsActive,
                    CASE WHEN gp.DoctorID IS NOT NULL THEN 'GENERAL' ELSE 'SPECIALIST' END AS DoctorType,
                    sp.SpecialtyID,sty.SpecialtyName
                    FROM DOCTOR d LEFT JOIN GENERAL_PRACTITIONED gp ON d.DoctorID=gp.DoctorID
                    LEFT JOIN SPECIALIST sp ON d.DoctorID=sp.DoctorID
                    LEFT JOIN SPECIALTY sty ON sty.SpecialtyID=sp.SpecialtyID'''
                + where + ' ORDER BY d.DoctorID DESC LIMIT %s OFFSET %s', args + (pg['per_page'], pg['offset']))
    return render_template('doctors.html', rows=data, pg=pg, q=q,
                           specialties=rows('SELECT SpecialtyID,SpecialtyName FROM SPECIALTY ORDER BY SpecialtyName'))


@app.post('/doctors/new')
@allow('ADMIN')
@safe_action
def doctor_create():
    name = required('full_name', 'Tên bác sĩ', 100)
    username = required('username', 'Username', 50)
    password = required('password', 'Mật khẩu', 100)
    license_no = required('license_number', 'Mã chứng chỉ', 50)
    dtype = required('doctor_type', 'Phân loại bác sĩ', 20)
    if dtype not in ('GENERAL', 'SPECIALIST') or len(password) < 8:
        raise InvalidInput('Phân loại hoặc mật khẩu không hợp lệ (tối thiểu 8 ký tự).')
    specialty = number('specialty_id', 'Chuyên khoa') if dtype == 'SPECIALIST' else None
    with write_tx() as cur:
        if specialty and not cur_one(cur, 'SELECT SpecialtyID FROM SPECIALTY WHERE SpecialtyID=%s', (specialty,)):
            raise InvalidInput('Chuyên khoa không tồn tại.')
        user_id = next_id(cur, 'USER_ACCOUNT')
        doctor_id = next_id(cur, 'DOCTOR')
        cur.execute('INSERT INTO USER_ACCOUNT (UserID,Username,PasswordHash,Role) VALUES (%s,%s,%s,%s)',
                    (user_id, username, generate_password_hash(password), 'DOCTOR'))
        cur.execute('''INSERT INTO DOCTOR (DoctorID,UserID,FullName,ContactInfo,LicenseNumber,IsActive)
                       VALUES (%s,%s,%s,%s,%s,1)''',
                    (doctor_id, user_id, name, request.form.get('contact_info') or None, license_no))
        if dtype == 'GENERAL':
            cur.execute('INSERT INTO GENERAL_PRACTITIONED (DoctorID) VALUES (%s)', (doctor_id,))
        else:
            cur.execute('INSERT INTO SPECIALIST (DoctorID,SpecialtyID) VALUES (%s,%s)', (doctor_id, specialty))
    flash(f'Đã thêm bác sĩ #{doctor_id} và phân loại {dtype}.', 'success')
    return redirect(url_for('doctors'))


@app.post('/doctors/<int:doctor_id>/edit')
@allow('ADMIN')
@safe_action
def doctor_edit(doctor_id):
    name = required('full_name', 'Tên bác sĩ', 100)
    license_no = required('license_number', 'Số chứng chỉ', 50)
    with write_tx() as cur:
        cur.execute('UPDATE DOCTOR SET FullName=%s,ContactInfo=%s,LicenseNumber=%s WHERE DoctorID=%s',
                    (name, request.form.get('contact_info', '').strip() or None, license_no, doctor_id))
        if not cur.rowcount:
            raise InvalidInput('Bác sĩ không tồn tại hoặc không có thay đổi.')
    flash('Đã cập nhật hồ sơ bác sĩ.', 'success')
    return redirect(url_for('doctors'))


@app.route('/accounts')
@allow('ADMIN')
def accounts():
    q = request.args.get('q', '').strip()[:50]
    where,args = (' WHERE ua.Username LIKE %s', (f'%{q}%',)) if q else ('', ())
    total = one('SELECT COUNT(*) total FROM USER_ACCOUNT ua' + where, args)['total']
    pg = page_info(total)
    data = rows('''SELECT ua.UserID,ua.Username,ua.Role, d.DoctorID, p.Patient,
                CASE WHEN d.DoctorID IS NOT NULL THEN d.FullName
                     WHEN p.Patient IS NOT NULL THEN p.FullName
                     ELSE 'Administrator' END AS ProfileName
                FROM USER_ACCOUNT ua
                LEFT JOIN DOCTOR d ON d.UserID=ua.UserID
                LEFT JOIN PATIENT p ON p.UserID=ua.UserID'''
                + where + ' ORDER BY ua.UserID DESC LIMIT %s OFFSET %s', args + (pg['per_page'],pg['offset']))
    return render_template('accounts.html', rows=data, pg=pg, q=q)


@app.post('/accounts/<int:user_id>/reset')
@allow('ADMIN')
@safe_action
def account_reset(user_id):
    password = required('password', 'Mật khẩu', 100)
    if len(password) < 8:
        raise InvalidInput('Mật khẩu mới phải có ít nhất 8 ký tự.')
    with write_tx() as cur:
        if not cur_one(cur, 'SELECT UserID FROM USER_ACCOUNT WHERE UserID=%s', (user_id,)):
            raise InvalidInput('Tài khoản không tồn tại.')
        cur.execute('UPDATE USER_ACCOUNT SET PasswordHash=%s WHERE UserID=%s',
                    (generate_password_hash(password), user_id))
    flash('Đã đặt lại mật khẩu bằng mã băm an toàn.', 'success')
    return redirect(url_for('accounts'))


@app.post('/doctors/<int:doctor_id>/archive')
@allow('ADMIN')
@safe_action
def doctor_archive(doctor_id):
    # Strictly implements: may archive when NO appointment IN PREVIOUS 30 DAYS.
    # Additionally protects future active bookings and all historical FK records.
    with write_tx() as cur:
        doctor = cur_one(cur, 'SELECT DoctorID,IsActive FROM DOCTOR WHERE DoctorID=%s FOR UPDATE', (doctor_id,))
        if not doctor:
            raise InvalidInput('Bác sĩ không tồn tại.')
        if not doctor['IsActive']:
            raise InvalidInput('Bác sĩ đã ngừng hoạt động.')
        counts = cur_one(cur, '''SELECT
            (SELECT COUNT(*) FROM APPOINTMENT
             WHERE DoctorID=%s AND AppointmentDateTime BETWEEN NOW()-INTERVAL 30 DAY AND NOW()) recent,
            (SELECT COUNT(*) FROM APPOINTMENT
             WHERE DoctorID=%s AND AppointmentDateTime>NOW()
               AND Status NOT IN ('Cancelled','No-show')) future_active''', (doctor_id, doctor_id))
        if counts['recent']:
            raise InvalidInput('Không được xóa: bác sĩ có lịch khám trong 30 ngày trước đó.')
        if counts['future_active']:
            raise InvalidInput('Không được xóa: bác sĩ còn lịch hẹn hoạt động trong tương lai.')
        cur.execute('UPDATE DOCTOR SET IsActive=0 WHERE DoctorID=%s', (doctor_id,))
    flash('Đã ngừng hoạt động bác sĩ (xóa mềm để bảo toàn lịch sử).', 'success')
    return redirect(url_for('doctors'))


@app.route('/schedules', methods=['GET'])
@allow('ADMIN')
def schedules():
    total = one('SELECT COUNT(*) total FROM DOCTOR_SCHEDULE')['total']
    pg = page_info(total)
    data = rows('''SELECT ds.*,d.FullName FROM DOCTOR_SCHEDULE ds
                  JOIN DOCTOR d ON ds.DoctorID=d.DoctorID
                  ORDER BY ds.ScheduleDate DESC,ds.StartTime LIMIT %s OFFSET %s''',
                (pg['per_page'], pg['offset']))
    ds_doctors = rows('SELECT DoctorID,FullName FROM DOCTOR WHERE IsActive=1 ORDER BY FullName')
    return render_template('schedules.html', rows=data, pg=pg, doctors=ds_doctors)


@app.post('/schedules/new')
@allow('ADMIN')
@safe_action
def schedule_create():
    doctor_id = number('doctor_id', 'Bác sĩ')
    day = required('date', 'Ngày làm việc', 10)
    start = required('start', 'Giờ bắt đầu', 5)
    end = required('end', 'Giờ kết thúc', 5)
    try:
        date.fromisoformat(day)
        start_time = datetime.strptime(start, '%H:%M').time()
        end_time = datetime.strptime(end, '%H:%M').time()
    except ValueError:
        raise InvalidInput('Ngày hoặc giờ không hợp lệ.')
    if start_time >= end_time:
        raise InvalidInput('Giờ kết thúc phải sau giờ bắt đầu.')
    status = request.form.get('status', 'Available')
    if status not in ('Available', 'Booked', 'Unavailable'):
        raise InvalidInput('Trạng thái ca không hợp lệ.')
    with write_tx() as cur:
        if not cur_one(cur, 'SELECT DoctorID FROM DOCTOR WHERE DoctorID=%s AND IsActive=1', (doctor_id,)):
            raise InvalidInput('Bác sĩ không hoạt động.')
        conflict = cur_one(cur, '''SELECT ScheduleID FROM DOCTOR_SCHEDULE
               WHERE DoctorID=%s AND ScheduleDate=%s
               AND StartTime < %s AND EndTime > %s LIMIT 1''', (doctor_id, day, end, start))
        if conflict:
            raise InvalidInput('BR24: Ca làm việc bị chồng giờ.')
        schedule_id = next_id(cur, 'DOCTOR_SCHEDULE')
        cur.execute('''INSERT INTO DOCTOR_SCHEDULE
                       (ScheduleID,DoctorID,ScheduleDate,StartTime,EndTime,AvailabilityStatus)
                       VALUES (%s,%s,%s,%s,%s,%s)''', (schedule_id, doctor_id, day, start, end, status))
    flash(f'Đã tạo ca làm việc #{schedule_id}.', 'success')
    return redirect(url_for('schedules'))


def active_schedules():
    return rows('''SELECT ds.ScheduleID,ds.DoctorID,ds.ScheduleDate,ds.StartTime,ds.EndTime,
                d.FullName FROM DOCTOR_SCHEDULE ds
                JOIN DOCTOR d ON d.DoctorID=ds.DoctorID
                WHERE d.IsActive=1 AND ds.AvailabilityStatus='Available'
                AND ds.ScheduleDate >= CURDATE()
                ORDER BY ds.ScheduleDate,ds.StartTime,ds.DoctorID LIMIT 500''')


def appointment_scope(role, profile_id):
    if role == 'DOCTOR':
        return ' WHERE a.DoctorID=%s', (profile_id,)
    if role == 'PATIENT':
        return ' WHERE a.Patient=%s', (profile_id,)
    return '', ()


@app.route('/appointments')
def appointments():
    where, args = appointment_scope(session['role'], session.get('profile_id'))
    total = one('SELECT COUNT(*) total FROM APPOINTMENT a' + where, args)['total']
    pg = page_info(total)
    data = rows('''SELECT a.AppointmentID,a.Patient,a.DoctorID,a.ScheduleID,a.AppointmentDateTime,
                a.EstimatedDuration,a.Modality,a.Status,v.PatientName,v.DoctorName
                FROM APPOINTMENT a JOIN vw_AppointmentDetails v ON a.AppointmentID=v.AppointmentID'''
                + where + ' ORDER BY a.AppointmentDateTime DESC,a.AppointmentID DESC LIMIT %s OFFSET %s',
                args + (pg['per_page'], pg['offset']))
    return render_template('appointments.html', rows=data, pg=pg)


@app.route('/appointments/new')
def appointment_new_form():
    if session['role'] not in ('ADMIN', 'DOCTOR', 'PATIENT'):
        abort(403)
    doctors_list = rows('SELECT DoctorID,FullName FROM DOCTOR WHERE IsActive=1 ORDER BY FullName')
    patients_list = rows('SELECT Patient,FullName FROM PATIENT ORDER BY Patient DESC LIMIT 80') if session['role'] == 'ADMIN' else []
    return render_template('appointment_form.html', action='new', item=None, doctors=doctors_list,
                           patients=patients_list, schedules=active_schedules())


def validate_appointment(cur, *, patient_id, doctor_id, schedule_id, start, duration, status, exclude_id=None):
    if status not in ('Scheduled', 'Checked-In', 'Completed', 'Cancelled', 'No-show'):
        raise InvalidInput('Trạng thái cuộc hẹn không hợp lệ.')
    if duration < 1 or duration > 240:
        raise InvalidInput('Thời lượng từ 1 đến 240 phút.')
    if not cur_one(cur, 'SELECT Patient FROM PATIENT WHERE Patient=%s', (patient_id,)):
        raise InvalidInput('Bệnh nhân không tồn tại.')
    if not cur_one(cur, 'SELECT DoctorID FROM DOCTOR WHERE DoctorID=%s AND IsActive=1', (doctor_id,)):
        raise InvalidInput('Bác sĩ không tồn tại hoặc ngừng hoạt động.')
    ds = cur_one(cur, 'SELECT * FROM DOCTOR_SCHEDULE WHERE ScheduleID=%s', (schedule_id,))
    if not ds or ds['DoctorID'] != doctor_id or ds['AvailabilityStatus'] != 'Available':
        raise InvalidInput('BR25/50: Ca làm việc phải Available và đúng bác sĩ.')
    begin = datetime.combine(ds['ScheduleDate'], (datetime.min + ds['StartTime']).time() if isinstance(ds['StartTime'], timedelta) else ds['StartTime'])
    finish = datetime.combine(ds['ScheduleDate'], (datetime.min + ds['EndTime']).time() if isinstance(ds['EndTime'], timedelta) else ds['EndTime'])
    if not begin <= start or start + timedelta(minutes=duration) > finish:
        raise InvalidInput('BR51: Lịch hẹn phải nằm trọn trong giờ làm việc đã chọn.')
    if status not in ('Cancelled', 'No-show'):
        conflict = cur_one(cur, '''SELECT AppointmentID FROM APPOINTMENT
            WHERE DoctorID=%s AND AppointmentID<>%s
              AND Status NOT IN ('Cancelled','No-show')
              AND AppointmentDateTime < %s
              AND DATE_ADD(AppointmentDateTime, INTERVAL EstimatedDuration MINUTE) > %s
            LIMIT 1''', (doctor_id, exclude_id or -1, start + timedelta(minutes=duration), start))
        if conflict:
            raise InvalidInput('BR34: Bác sĩ đã có lịch khám trùng khung giờ.')


def appointment_values(cur, editing=None):
    role, own_id = session['role'], session.get('profile_id')
    patient_id = own_id if role == 'PATIENT' else number('patient_id', 'Mã bệnh nhân')
    doctor_id = own_id if role == 'DOCTOR' else number('doctor_id', 'Mã bác sĩ')
    schedule_id = number('schedule_id', 'Ca làm việc')
    duration = number('duration', 'Thời lượng')
    modality = required('modality', 'Hình thức', 20)
    if modality not in ('In-person', 'Telemedicine'):
        raise InvalidInput('Hình thức khám không hợp lệ.')
    try:
        start = datetime.fromisoformat(required('start', 'Ngày giờ khám', 30))
    except ValueError:
        raise InvalidInput('Ngày giờ khám không hợp lệ.')
    status = (request.form.get('status', 'Scheduled') if role == 'ADMIN' else 'Scheduled')
    if status == 'Completed':
        raise InvalidInput('Chỉ hoàn thành lịch qua chức năng Kết thúc khám.')
    validate_appointment(cur, patient_id=patient_id, doctor_id=doctor_id,
                         schedule_id=schedule_id, start=start, duration=duration, status=status,
                         exclude_id=editing)
    return patient_id,doctor_id,schedule_id,start,duration,modality,status


@app.post('/appointments/new')
@allow('ADMIN', 'DOCTOR', 'PATIENT')
@safe_action
def appointment_create():
    with write_tx() as cur:
        vals = appointment_values(cur)
        appointment_id = next_id(cur, 'APPOINTMENT')
        cur.execute('''INSERT INTO APPOINTMENT
            (AppointmentID,Patient,DoctorID,ScheduleID,PrecedingAppointmentID,
             AppointmentDateTime,EstimatedDuration,Modality,Status,CreatedBy)
            VALUES (%s,%s,%s,%s,NULL,%s,%s,%s,%s,%s)''',
                    (appointment_id, *vals, session['role']))
    flash(f'Đặt lịch #{appointment_id} thành công.', 'success')
    return redirect(url_for('appointments'))


@app.route('/appointments/<int:appointment_id>/edit')
@allow('ADMIN')
def appointment_edit_form(appointment_id):
    item = one('SELECT * FROM APPOINTMENT WHERE AppointmentID=%s', (appointment_id,))
    if not item:
        abort(404)
    if item['Status'] == 'Completed':
        flash('Không chỉnh sửa trực tiếp lịch khám đã hoàn thành.', 'warning')
        return redirect(url_for('appointments'))
    return render_template('appointment_form.html', item=item, action='edit',
                           doctors=rows('SELECT DoctorID,FullName FROM DOCTOR WHERE IsActive=1 ORDER BY FullName'),
                           patients=rows('SELECT Patient,FullName FROM PATIENT ORDER BY Patient DESC LIMIT 80'),
                           schedules=active_schedules())


@app.post('/appointments/<int:appointment_id>/edit')
@allow('ADMIN')
@safe_action
def appointment_edit(appointment_id):
    with write_tx() as cur:
        item = cur_one(cur, 'SELECT * FROM APPOINTMENT WHERE AppointmentID=%s FOR UPDATE', (appointment_id,))
        if not item:
            raise InvalidInput('Không tìm thấy lịch khám.')
        if item['Status'] == 'Completed' or cur_one(cur, 'SELECT SessionID FROM CONSULTATION_SESSION WHERE AppointmentID=%s', (appointment_id,)):
            raise InvalidInput('Không sửa lịch đã có phiên khám/lịch sử.')
        vals = appointment_values(cur, editing=appointment_id)
        cur.execute('''UPDATE APPOINTMENT SET Patient=%s,DoctorID=%s,ScheduleID=%s,
            AppointmentDateTime=%s,EstimatedDuration=%s,Modality=%s,Status=%s WHERE AppointmentID=%s''',
                    (*vals, appointment_id))
    flash('Đã sửa lịch và kiểm tra lại các quy tắc xung đột.', 'success')
    return redirect(url_for('appointments'))


@app.post('/appointments/<int:appointment_id>/delete')
@allow('ADMIN')
@safe_action
def appointment_delete(appointment_id):
    with write_tx() as cur:
        item = cur_one(cur, 'SELECT AppointmentID,Status FROM APPOINTMENT WHERE AppointmentID=%s FOR UPDATE', (appointment_id,))
        if not item:
            raise InvalidInput('Lịch khám không tồn tại.')
        if item['Status'] == 'Completed':
            raise InvalidInput('Không xóa lịch đã hoàn thành, cần giữ lịch sử y tế.')
        related = cur_one(cur, '''SELECT
            (SELECT COUNT(*) FROM CONSULTATION_SESSION WHERE AppointmentID=%s) s,
            (SELECT COUNT(*) FROM APPOINTMENT WHERE PrecedingAppointmentID=%s) following''',
            (appointment_id, appointment_id))
        if any(related.values()):
            raise InvalidInput('Không thể xóa lịch đã có phiên khám hoặc lịch tái khám liên kết.')
        cur.execute('DELETE FROM APPOINTMENT WHERE AppointmentID=%s', (appointment_id,))
    flash('Đã xóa lịch khám chưa phát sinh dữ liệu liên kết.', 'success')
    return redirect(url_for('appointments'))


@app.post('/appointments/<int:appointment_id>/complete')
@allow('ADMIN', 'DOCTOR')
@safe_action
def appointment_complete(appointment_id):
    notes = request.form.get('notes', '').strip()[:3000] or None
    with write_tx() as cur:
        ap = cur_one(cur, 'SELECT * FROM APPOINTMENT WHERE AppointmentID=%s FOR UPDATE', (appointment_id,))
        if not ap:
            raise InvalidInput('Lịch khám không tồn tại.')
        if session['role'] == 'DOCTOR' and ap['DoctorID'] != session['profile_id']:
            abort(403)
        if ap['Status'] not in ('Scheduled', 'Checked-In'):
            raise InvalidInput('Chỉ hoàn thành lịch đang Scheduled/Checked-In.')
        if ap['AppointmentDateTime'] > datetime.now():
            raise InvalidInput('Không thể hoàn thành buổi khám chưa diễn ra.')
        if cur_one(cur, 'SELECT SessionID FROM CONSULTATION_SESSION WHERE AppointmentID=%s', (appointment_id,)):
            raise InvalidInput('Buổi khám đã có phiên tư vấn.')
        sid = next_id(cur, 'CONSULTATION_SESSION')
        minutes = ap['EstimatedDuration']
        cur.execute('''INSERT INTO CONSULTATION_SESSION
            (SessionID,AppointmentID,StartTime,EndTime,ActualDuration,SessionType,ClinicalNotes,MeetingURL)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (sid, appointment_id, ap['AppointmentDateTime'],
             ap['AppointmentDateTime'] + timedelta(minutes=minutes),minutes,
             'Virtual' if ap['Modality'] == 'Telemedicine' else 'In-person',
             notes, None))
        cur.execute("UPDATE APPOINTMENT SET Status='Completed' WHERE AppointmentID=%s", (appointment_id,))
    flash(f'Đã hoàn thành khám; SessionID={sid}. Có thể kê đơn.', 'success')
    return redirect(url_for('prescription_create_form'))


def prescription_filter():
    if session['role'] == 'DOCTOR':
        return ' WHERE pr.DoctorID=%s', (session['profile_id'],)
    if session['role'] == 'PATIENT':
        return ' WHERE pr.Patient=%s', (session['profile_id'],)
    return '', ()


@app.route('/prescriptions')
def prescriptions():
    where, args = prescription_filter()
    total = one('SELECT COUNT(*) total FROM PRESCRIPTION pr' + where, args)['total']
    pg = page_info(total)
    data = rows('''SELECT pr.PrescriptionID,pr.IssueDate,p.FullName AS PatientName,
                d.FullName AS DoctorName,COUNT(pi.PrescriptionItemID) AS ItemCount
                FROM PRESCRIPTION pr JOIN PATIENT p ON p.Patient=pr.Patient
                JOIN DOCTOR d ON d.DoctorID=pr.DoctorID
                LEFT JOIN PRESCRIPTION_ITEM pi ON pi.PrescriptionID=pr.PrescriptionID'''
                + where + ''' GROUP BY pr.PrescriptionID,pr.IssueDate,p.FullName,d.FullName
                ORDER BY pr.IssueDate DESC,pr.PrescriptionID DESC LIMIT %s OFFSET %s''',
                args + (pg['per_page'], pg['offset']))
    return render_template('prescriptions.html', rows=data, pg=pg)


@app.route('/prescriptions/<int:prescription_id>')
def prescription_detail(prescription_id):
    pr = one('''SELECT pr.*,p.FullName PatientName,d.FullName DoctorName
                FROM PRESCRIPTION pr JOIN PATIENT p ON p.Patient=pr.Patient
                JOIN DOCTOR d ON d.DoctorID=pr.DoctorID WHERE pr.PrescriptionID=%s''', (prescription_id,))
    if not pr:
        abort(404)
    if session['role'] == 'PATIENT' and pr['Patient'] != session['profile_id']:
        abort(403)
    if session['role'] == 'DOCTOR' and pr['DoctorID'] != session['profile_id']:
        abort(403)
    # View 2 is the canonical source for medication rows.
    items = rows('''SELECT MedicationName,Dosage,Frequency,Duration,SpecialInstructions
                    FROM vw_PrescriptionDetails WHERE PrescriptionID=%s''', (prescription_id,))
    return render_template('prescription_detail.html', pr=pr, items=items)


@app.route('/prescriptions/new')
@allow('ADMIN', 'DOCTOR')
def prescription_create_form():
    doctor_only = session['role'] == 'DOCTOR'
    candidates = rows('''SELECT s.SessionID,a.AppointmentID,a.DoctorID,a.Patient,
                p.FullName PatientName,d.FullName DoctorName
                FROM CONSULTATION_SESSION s JOIN APPOINTMENT a ON a.AppointmentID=s.AppointmentID
                JOIN PATIENT p ON p.Patient=a.Patient JOIN DOCTOR d ON d.DoctorID=a.DoctorID
                WHERE a.Status='Completed' ''' + ('AND a.DoctorID=%s ' if doctor_only else '') +
                'ORDER BY s.SessionID DESC LIMIT 250', (session['profile_id'],) if doctor_only else ())
    medications = rows('SELECT MedicationID,MedicationName FROM MEDICATION ORDER BY MedicationName')
    return render_template('prescription_form.html', candidates=candidates, medications=medications)


@app.post('/prescriptions/new')
@allow('ADMIN', 'DOCTOR')
@safe_action
def prescription_create():
    session_id = number('session_id', 'Mã phiên khám')
    medication_ids = request.form.getlist('medication_id')
    doses = request.form.getlist('dosage')
    freqs = request.form.getlist('frequency')
    durations = request.form.getlist('duration')
    instructions = request.form.getlist('instructions')
    if not medication_ids or len(medication_ids) > 5 or not (
        len(medication_ids) == len(doses) == len(freqs) == len(durations) == len(instructions)):
        raise InvalidInput('Đơn thuốc cần từ 1 đến 5 thuốc và đủ thông tin.')
    with write_tx() as cur:
        ap = cur_one(cur, '''SELECT a.Patient,a.DoctorID,a.Status
                FROM CONSULTATION_SESSION s JOIN APPOINTMENT a ON a.AppointmentID=s.AppointmentID
                WHERE s.SessionID=%s''', (session_id,))
        if not ap or ap['Status'] != 'Completed':
            raise InvalidInput('Chỉ kê đơn cho phiên khám Completed tồn tại.')
        if session['role'] == 'DOCTOR' and ap['DoctorID'] != session['profile_id']:
            abort(403)
        for med_id, dose, freq, length in zip(medication_ids, doses, freqs, durations):
            try:
                med = int(med_id)
            except ValueError:
                raise InvalidInput('Mã thuốc không hợp lệ.')
            if not cur_one(cur, 'SELECT MedicationID FROM MEDICATION WHERE MedicationID=%s', (med,)):
                raise InvalidInput('Có mã thuốc không tồn tại.')
            if not dose.strip() or not freq.strip() or not length.strip():
                raise InvalidInput('Thuốc cần đủ liều, tần suất, thời lượng.')
            if max(len(dose),len(freq),len(length)) > 50:
                raise InvalidInput('Các trường liều/tần suất/thời lượng tối đa 50 ký tự.')
        prescription_id = next_id(cur, 'PRESCRIPTION')
        cur.execute('''INSERT INTO PRESCRIPTION (PrescriptionID,Patient,DoctorID,SessionID,IssueDate)
                       VALUES (%s,%s,%s,%s,CURDATE())''',
                    (prescription_id, ap['Patient'], ap['DoctorID'], session_id))
        first_item_id = next_id(cur, 'PRESCRIPTION_ITEM')
        for i, med_id in enumerate(medication_ids):
            cur.execute('''INSERT INTO PRESCRIPTION_ITEM
                (PrescriptionItemID,PrescriptionID,MedicationID,Dosage,Frequency,Duration,SpecialInstructions)
                VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                (first_item_id+i, prescription_id,int(med_id),doses[i].strip(),freqs[i].strip(),
                 durations[i].strip(), instructions[i].strip()[:2000] or None))
    flash(f'Đã kê đơn #{prescription_id} với {len(medication_ids)} thuốc.', 'success')
    return redirect(url_for('prescription_detail', prescription_id=prescription_id))


@app.post('/prescriptions/<int:prescription_id>/delete')
@allow('ADMIN')
@safe_action
def prescription_delete(prescription_id):
    with write_tx() as cur:
        if not cur_one(cur, 'SELECT PrescriptionID FROM PRESCRIPTION WHERE PrescriptionID=%s FOR UPDATE', (prescription_id,)):
            raise InvalidInput('Không tìm thấy đơn thuốc.')
        cur.execute('DELETE FROM PRESCRIPTION_ITEM WHERE PrescriptionID=%s', (prescription_id,))
        cur.execute('DELETE FROM PRESCRIPTION WHERE PrescriptionID=%s', (prescription_id,))
    flash('Đã xóa đơn thuốc và toàn bộ chi tiết liên quan.', 'success')
    return redirect(url_for('prescriptions'))


@app.errorhandler(403)
def forbidden(_exc):
    return render_template('error.html', message='Bạn không có quyền thực hiện thao tác này.', code=403), 403


@app.errorhandler(404)
def not_found(_exc):
    return render_template('error.html', message='Không tìm thấy nội dung.', code=404), 404


@app.errorhandler(400)
def bad_request(exc):
    return render_template('error.html', message=str(exc.description), code=400), 400


@app.errorhandler(Error)
def db_error(exc):
    app.logger.exception('MySQL error outside form handler')
    return render_template('error.html', message='Không thể truy vấn MySQL. Kiểm tra bảng/Views và kết nối.', code=500), 500


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', '0') == '1')
