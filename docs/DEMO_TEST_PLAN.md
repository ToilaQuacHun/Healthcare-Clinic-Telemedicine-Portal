# MediConnect Phase 4 — Demo & acceptance checklist

Test on a disposable **copy of Phrase3**. Capture browser screenshots and MySQL Workbench results.

## A. Authentication and roles

| ID | Scenario | Expected |
|---|---|---|
| AUTH01 | Logged out user visits `/` | Redirects to `/login` |
| AUTH02 | Wrong username or password | Error, no logged-in session |
| AUTH03 | Admin login | Dashboard and all admin navigation |
| AUTH04 | Doctor login with linked `DOCTOR.UserID` | Only own appointments / prescriptions |
| AUTH05 | Patient login with linked `PATIENT.UserID` | Only own appointments / prescriptions |
| AUTH06 | Doctor types `/patients` or `/accounts` | 403 |
| AUTH07 | Patient opens another patient's prescription URL | 403 |
| AUTH08 | Logout then visit previous page | Redirect to login |

## B. Appointment and SQL business rules

| ID | Scenario | Expected |
|---|---|---|
| AP01 | Admin creates an Available schedule | New `DOCTOR_SCHEDULE` row |
| AP02 | Schedule overlaps doctor's other schedule | Rejected BR24 |
| AP03 | Patient creates valid appointment | New `APPOINTMENT`; View 1 shows it |
| AP04 | Doctor creates appointment for patient | New appointment with `CreatedBy='DOCTOR'` |
| AP05 | Admin creates valid appointment | New appointment with `CreatedBy='ADMIN'` |
| AP06 | Same doctor overlapping Scheduled appointment | Rejected by app + `trg_prevent_overlap` |
| AP07 | Appointment outside the selected schedule | Rejected by app + `trg_validate_appointment_schedule` |
| AP08 | Wrong doctor for schedule | Rejected |
| AP09 | Admin edits appointment into overlap | Rejected by app (existing DB triggers are INSERT-only) |
| AP10 | Admin deletes appointment without consultations/follow-ups | Deleted |
| AP11 | Admin tries to delete completed/linked appointment | Blocked |
| AP12 | Doctor finishes own past appointment | `CONSULTATION_SESSION` created, `APPOINTMENT.Status=Completed` |
| AP13 | Doctor finishes another doctor's appointment | Forbidden 403 |

## C. Prescription

| ID | Scenario | Expected |
|---|---|---|
| RX01 | Doctor prescribes for own Completed session | `PRESCRIPTION` & item rows created |
| RX02 | Doctor prescribes for another doctor's session | Forbidden 403 |
| RX03 | Prescribe against Scheduled / no session | Rejected |
| RX04 | Patient views own prescription | View 2 details shown |
| RX05 | Admin removes prescription | Prescription items removed first; parent deleted |

## D. Doctor and patient deletion

| ID | Scenario | Expected |
|---|---|---|
| DEL01 | Patient with appointment / Rx | Patient delete blocked |
| DEL02 | Patient with no history links | Patient + linked PATIENT account removed |
| DEL03 | Doctor with appointment within past 30 days | Archive blocked |
| DEL04 | Doctor with active future appointment | Archive blocked |
| DEL05 | Doctor with no appointments past 30 days & no active future appointment | `IsActive=0` (soft delete), old history preserved |

## E. Show original Phase 3 objects

```sql
USE Phrase3;
SHOW FULL TABLES;
SELECT TRIGGER_NAME, EVENT_MANIPULATION FROM INFORMATION_SCHEMA.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE();
SELECT * FROM vw_AppointmentDetails LIMIT 10;
SELECT * FROM vw_PrescriptionDetails LIMIT 10;
SHOW INDEX FROM APPOINTMENT;
```

Record actual outcomes; do not mark a test PASS until running it on MySQL.
