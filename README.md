# MediConnect Phase 4 – Full demo project

**Flask + Jinja HTML + MySQL `Phrase3`**, no separate REST API or Postman required.

> **Educational demo only.** This is not a deployable health-care service. Use synthetic data, not medical information about real people. Protect the database and never commit `.env` or passwords to GitHub.

## Implemented features

| Feature | Admin | Doctor | Patient |
|---|:---:|:---:|:---:|
| Login / Logout | Yes | Yes | Yes |
| Dashboard (all data) | Yes | - | - |
| View appointments | All | Own doctor ID | Own patient ID |
| Create appointments | Yes | Yes | Yes |
| Edit / delete appointments | Yes | - | - |
| Mark visit completed (creates Consultation Session) | Yes | Own | - |
| View prescriptions | All | Own prescriptions | Own prescriptions |
| Create prescriptions for completed consultation | Yes | Own completed visit | - |
| Delete prescription & items | Yes | - | - |
| Create & update patients | Yes | - | - |
| Delete patient with no linked appointment / prescription / history | Yes | - | - |
| Create doctor, GP or specialist + specialty | Yes | - | - |
| Archive doctor subject to 30-day rule | Yes | - | - |
| Create doctor schedule (no overlapping shift) | Yes | - | - |
| Database pagination | Yes | Yes | Yes |

Special rules:

- Both existing **BEFORE INSERT** appointment triggers remain active. On edits the Flask backend explicitly rechecks schedule/day/doctor and overlap (existing UPDATE trigger is not assumed).
- `ADMIN`, `DOCTOR`, `PATIENT` role-based filtering is enforced on SQL queries/server routes, not only on the menu.
- Doctor deletion means **archive/soft-delete** (`DOCTOR.IsActive=0`) to retain historical visits and prescriptions. A doctor is eligible **only if no appointment occurred in the last 30 days**, and the app also requires **no active future appointments**. **No physical `DELETE DOCTOR`** is performed because historic tables have foreign keys.
- Patient deletion is physical and allowed only when they have **no appointment, no prescription, no medical history**; otherwise blocked.
- Appointment deletion is allowed only without a consultation session or follow-up appointment, and not once Completed.
- Prescription deletion removes child `PRESCRIPTION_ITEM` records first in the same transaction.
- New passwords are securely hashed. Some *old Phase 3 test accounts* have plaintext passwords; the app accepts them **only for local demo** and immediately upgrades their hash. Accounts with `DEMO_DISABLED_` remain disabled until reset with the demo account script.

## Start in macOS VS Code (Python 3.13 recommended)

**1. Back up `Phrase3` in MySQL Workbench** (Server > Data Export), ideally restore a copy for demos. Import the Phase 3 dataset separately if it is not present. This ZIP **does not replace** your existing tables, 11k data, triggers or views.

**2. Open** `MediConnect-Phase4-Full` in VS Code.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env`: set `DB_USER`, `DB_PASSWORD`, `DB_NAME=Phrase3`, and paste the random value into `FLASK_SECRET_KEY`.

**3. Apply database migration** in MySQL Workbench, **once**:

- `scripts/01_upgrade_existing_phrase3.sql`: adds only `DOCTOR.IsActive` to the existing table if missing; keeps all 13 tables and all existing records. Running twice does not add the column twice.
- `scripts/02_check_existing_data.sql`: checks counts/views/triggers; optional.

This version relies on the original schema (see included `docs/SCHEMA_NOTES.md`). It assumes both Views exist (`vw_AppointmentDetails`, `vw_PrescriptionDetails`) and previous 2 triggers are present.

**4. Create demo logins** if none are known (use only on a copy with synthetic data):

```bash
python scripts/setup_demo_accounts.py --role ADMIN --username mcadmin_demo
```

For Doctor / Patient, choose *actual* IDs from Workbench:

```sql
SELECT DoctorID, UserID, FullName FROM DOCTOR WHERE IsActive=1 ORDER BY DoctorID LIMIT 10;
SELECT Patient, UserID, FullName FROM PATIENT ORDER BY Patient LIMIT 10;
```

Then run (replace the IDs):

```bash
python scripts/setup_demo_accounts.py --role DOCTOR --profile-id 1
python scripts/setup_demo_accounts.py --role PATIENT --profile-id 1
```

For accounts already linked, this command asks you to confirm password reset; it **does not change the existing username**. The script displays which username to use.

**5. Run**:

```bash
python -c "from db import get_connection; c=get_connection(); print('Connected:',c.database); c.close()"
python app.py
```

Open `http://127.0.0.1:5000`. Users without a session are redirected to `/login`.

## Walkthrough for the lecturer

1. Login as **ADMIN**: Dashboard live record counts; show Patients and Doctors with paging, add a new GP then a new Specialist with specialty.
2. Create a doctor schedule for today or a later date and set `Available`; go to Create Appointment. Verify a valid appointment succeeds and a conflicting appointment is **rejected by existing MySQL trigger**.
3. Login as **PATIENT**: only this patient's appointments are shown; patient can book appointment.
4. Login as **DOCTOR**: only own appointments and prescriptions are listed; a doctor can book a visit too. For an appointment in the past, use `Hoàn thành khám` to add a consultation session (if not already Completed), then prescribe medication using its SessionID. Patient can view their own prescription afterward.
5. Login as **ADMIN**: edit or delete a safe appointment; delete prescription with detail rows; try to delete a patient with appointments (blocked), and archive doctor with an appointment in the past 30 days (blocked). Try an eligible doctor (archived without deleting historical rows).
6. In Workbench show the original Views and Triggers, and compare UI with SQL query results.

## Known limitations and safety notes

- Not live-tested against your **current** MySQL instance; schema was matched against the uploaded `tables.sql` dump and earlier Phase 3 definitions. Test on a backup and inspect Terminal errors before treating it as final.
- Authentication and authorization are designed for local class demos; it still needs login throttling, session management and audit logging to be production-ready. Do not deploy to the public Internet.
- Flask's built-in development server (`FLASK_DEBUG=1`) is local-only; turn off in any public deployment.
- The app serializes its own writes with MySQL `GET_LOCK` because original primary keys are integer **without AUTO_INCREMENT**. Other direct SQL clients are not protected by this app lock. A robust deployed version should switch to DB sequences/auto increment (after reviewing data IDs).
- Doctor schedule dropdown shows up to 500 upcoming Available schedules. Create a fresh schedule using Admin if no suitable option exists.
- Session completion is implemented for scheduled/past appointments only. Prescriptions require a **Completed** appointment and a valid consultation session. Telemedicine sessions are created as `Virtual`.
- Pagination reads only 10/20/50/100 records at a time; MySQL always retains all records.
- This code is not a medical prescribing tool; sample doses are manually entered for demonstrating relational data only.
