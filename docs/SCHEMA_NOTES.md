# Database schema compatibility

Grounded against provided MySQL `tables.sql` dump (server 8.4.11, schema name `Phrase3`).

Original 13 tables: `USER_ACCOUNT`, `PATIENT`, `DOCTOR`, `GENERAL_PRACTITIONED`, `SPECIALIST`, `SPECIALTY`, `DOCTOR_SCHEDULE`, `APPOINTMENT`, `CONSULTATION_SESSION`, `MEDICAL_HISTORY`, `MEDICATION`, `PRESCRIPTION`, `PRESCRIPTION_ITEM`.

All original PKs are `int NOT NULL` **without `AUTO_INCREMENT`**. App inserts explicit sequential IDs using a cross-route MySQL advisory lock. Preserve the original 13 tables and two Views:

- `vw_AppointmentDetails` – expected `AppointmentID`, `PatientName`, `DoctorName`, `AppointmentDateTime`, `EstimatedDuration`, `Modality`, `Status`.
- `vw_PrescriptionDetails` – expected `PrescriptionID`, `PatientName`, `DoctorName`, `IssueDate`, `MedicationName`, `Dosage`, `Frequency`, `Duration`, `SpecialInstructions`.

App SQL uses the original misspelling `GENERAL_PRACTITIONED`, and the original `PATIENT.Patient` PK; do not rename these.

The **only schema upgrade** is `ALTER DOCTOR ADD IsActive TINYINT NOT NULL DEFAULT 1`, performed safely by `scripts/01_upgrade_existing_phrase3.sql`. This supports soft-deletion preserving existing FKs.

Existing **BEFORE INSERT** triggers remain in place (not replaced). The app implements additional checks on edit, but to enforce UPDATE in SQL Workbench too, the Phase 3 database would need separately designed BEFORE UPDATE triggers.

The application is server-rendered; no REST API required.
