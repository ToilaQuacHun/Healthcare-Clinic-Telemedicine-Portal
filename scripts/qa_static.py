"""Offline structural smoke-test. No MySQL and no Flask server required.

Run from project folder: python scripts/qa_static.py
Requires jinja2 (installed as Flask dependency).
"""
import ast
from datetime import date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import jinja2

ROOT = Path(__file__).resolve().parents[1]
for file in list(ROOT.glob('*.py')) + list((ROOT/'scripts').glob('*.py')):
    ast.parse(file.read_text())

jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(ROOT/'templates'), autoescape=True)
jinja.globals.update(url_for=lambda x,**kwargs: '/' + x, csrf_token=lambda: 'sample-csrf', current_year=2026, get_flashed_messages=lambda **kwargs: [])
request = SimpleNamespace(endpoint='dashboard')
pg = dict(total=1000,pages=50,page=1,per_page=20,offset=0,window=range(1,4))
base = dict(session={'role':'ADMIN','profile_id':1,'username':'demo','user_id':1},request=request,pg=pg,q='',current_year=2026, get_flashed_messages=lambda **kwargs: [])
ap = dict(AppointmentID=123,Patient=7,DoctorID=8,ScheduleID=9,AppointmentDateTime=datetime(2026,11,1,8),EstimatedDuration=30,
          PatientName='Demo Patient',DoctorName='Demo Doctor',Modality='In-person',Status='Scheduled')
patient=dict(Patient=7,UserID=10,FullName='Demo Patient',BloodType='O+',EmergencyContact='000')
doctor=dict(DoctorID=8,FullName='Demo Doctor',ContactInfo='demo',LicenseNumber='TEST-001',IsActive=1,DoctorType='GENERAL',SpecialtyName=None)
schedule=dict(ScheduleID=9,DoctorID=8,FullName='Demo Doctor',ScheduleDate=date(2026,11,1),StartTime=timedelta(hours=8),EndTime=timedelta(hours=12),AvailabilityStatus='Available')
prescription=dict(PrescriptionID=33,IssueDate=date(2026,11,1),Patient=7,DoctorID=8,PatientName='Demo Patient',DoctorName='Demo Doctor',SessionID=17,ItemCount=1)
contexts = {
 'login.html':dict(session={},request=request),
 'dashboard.html':dict(base,counts=dict(patients=1000,doctors=100,appointments=2500,prescriptions=800),latest=[ap]),
 'patients.html':dict(base,rows=[patient]),
 'doctors.html':dict(base,rows=[doctor],specialties=[dict(SpecialtyID=1,SpecialtyName='Internal Medicine')]),
 'accounts.html':dict(base,rows=[dict(UserID=10,Username='doctor-demo',Role='DOCTOR',ProfileName='Demo Doctor')]),
 'schedules.html':dict(base,rows=[schedule],doctors=[doctor]),
 'appointments.html':dict(base,rows=[ap]),
 'appointment_form.html':dict(base,item=None,action='new',doctors=[doctor],patients=[patient],schedules=[schedule]),
 'prescriptions.html':dict(base,rows=[prescription]),
 'prescription_detail.html':dict(base,pr=prescription,items=[dict(MedicationName='Example medicine',Dosage='1',Frequency='2/day',Duration='3 days',SpecialInstructions='Sample')]),
 'prescription_form.html':dict(base,candidates=[dict(SessionID=17,AppointmentID=123,PatientName='Demo Patient',DoctorName='Demo Doctor')],medications=[dict(MedicationID=1,MedicationName='Example')]),
 'error.html':dict(base,code=403,message='Not permitted'),
}
for template in (ROOT/'templates').glob('*.html'):
    jinja.parse(template.read_text())
for name,context in contexts.items():
    output=jinja.get_template(name).render(**context)
    assert '<html' in output or '<!doctype' in output.lower(), name
    print('OK',name,len(output),'bytes')
print('PASS: Python syntax and all',len(contexts),'HTML views rendered with dummy records')
