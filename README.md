# MediConnect: Integrated Healthcare Clinic & Telemedicine Management System

## Database Project Report

**Due Date:** [Insert Date - Week ….]  
**Project ID & Title:** Healthcare Clinic & Telemedicine Portal

---

## A. Project Identity

### Team Name

**G2**

### Team Members

- Lê Nguyễn Quốc Hùng — n24dece070@student.ptithcm.edu.vn
- Trần Hoàng Hải Đăng — n24dece059@student.ptithcm.edu.vn
- Trần Quốc Huy — n24dece074@student.ptithcm.edu.vn

### Project Title

**MediConnect: Integrated Healthcare Clinic & Telemedicine Management System**

---

# 1. Introduction & Project Scope

*Adapted from ISO/IEC/IEEE 29148*

The Healthcare Clinic & Telemedicine Portal is a centralized database system designed to support comprehensive healthcare information management, clinical workflow coordination, and administrative operations for a clinic providing both traditional in-person consultations and telemedicine services.

The system manages:

- Multi-role user authentication and access control
- Patient profiles
- Doctor information
- Doctor schedules
- Appointment booking
- Follow-up appointments
- Consultation sessions
- Medical histories
- Digital prescriptions

The system is intended to keep healthcare information consistent, secure, accurate, and reliable. It also prevents scheduling conflicts and enforces strong relationships among doctors, schedules, appointments, consultation sessions, medical histories, and prescriptions.

Role-Based Access Control (**RBAC**) is applied with three main roles:

- `ADMIN`
- `DOCTOR`
- `PATIENT`

General Practitioners and Specialists share common doctor information, so `DOCTOR` is modeled as a supertype with `GENERAL_PRACTITIONER` and `SPECIALIST` as **Total and Disjoint** subtypes.

---

## 1.1 System Objective

The main objective of the system is to provide a reliable database for storing and managing the essential information of a healthcare clinic.

- Manage user credentials and enforce Role-Based Access Control (RBAC) across ADMIN, DOCTOR, and PATIENT roles.
- Maintain centralized patient profiles containing demographic, contact, emergency contact, and baseline clinical information.
- Manage doctor information and professional credentials.
- Distinguish General Practitioners from Specialists using Total and Disjoint EER specialization.
- Link medical specialists to their corresponding clinical specialties.
- Manage doctors' working schedules and availability while preventing overlapping schedule slots.
- Coordinate appointment bookings and support patient self-booking, administrator-assisted booking, and doctor-created follow-up appointments.
- Manage consultation sessions and enforce that each consultation session is based on a valid appointment.
- Record actual consultation start time, end time, duration, modality, and clinical notes.
- Maintain longitudinal medical history and diagnosis records.
- Manage prescriptions issued by attending doctors during valid clinical sessions.
- Maintain data integrity and prevent inconsistent healthcare records.
- Provide a rigorous conceptual database model for later logical design, SQL implementation, and Python web development.

---

# 1.2 Business Rules & Constraints

## 1.2.1 User Account

- **BR1:** Each user account must have a unique `UserID`.
- **BR2:** Each user account must have a unique, non-null `Username` and a secure password hash.
- **BR3:** Every account must be assigned exactly one role: `ADMIN`, `DOCTOR`, or `PATIENT`.
- **BR4:** Every registered doctor and patient must be linked to exactly one valid `USER_ACCOUNT`.
- **BR5:** An account cannot be deleted while active dependent operational records require it.

## 1.2.2 Patient

- **BR6:** Each patient must have a unique `PatientID`.
- **BR7:** Each patient must have basic identifying and contact information.
- **BR8:** A patient profile records baseline health information including blood type, allergies, chronic diseases, and emergency contact information.
- **BR9:** A patient can have zero, one, or many appointments over time.
- **BR10:** Each appointment belongs to exactly one patient.
- **BR11:** A patient can participate in zero, one, or many consultation sessions.
- **BR12:** A patient can have multiple medical history records and multiple prescriptions.

## 1.2.3 Doctor and Medical Staff

- **BR13:** Each doctor must have a unique `DoctorID`.
- **BR14:** Each doctor must have full name, contact information, and a unique `LicenseNumber`.
- **BR15:** Every doctor must be classified as either a General Practitioner or a Specialist.
- **BR16:** `GENERAL_PRACTITIONER` is a subtype of `DOCTOR`.
- **BR17:** `SPECIALIST` is a subtype of `DOCTOR`.
- **BR18:** Each Specialist must be associated with exactly one `SPECIALTY`.
- **BR19:** `GENERAL_PRACTITIONER` and `SPECIALIST` are disjoint; a doctor cannot belong to both.
- **BR20:** The specialization is total; every `DOCTOR` belongs to one of the two subtypes.

## 1.2.4 Doctor Schedule

- **BR21:** A doctor can have zero, one, or many schedule records.
- **BR22:** Each schedule record belongs to exactly one doctor.
- **BR23:** Each schedule specifies `ScheduleDate`, `StartTime`, `EndTime`, and `AvailabilityStatus`.
- **BR24:** A doctor must not have overlapping working schedule periods on the same date.
- **BR25:** An appointment may only use an active and available working schedule.

## 1.2.5 Appointment

- **BR26:** Each appointment must have a unique `AppointmentID`.
- **BR27:** Each appointment must be associated with exactly one patient and exactly one doctor.
- **BR28:** An appointment can be created by a patient, ADMIN, or assigned DOCTOR according to system permissions.
- **BR29:** Each appointment must specify date/time, estimated duration, and modality: `In-person` or `Telemedicine`.
- **BR30:** Status must be `Scheduled`, `Checked-In`, `Completed`, `Cancelled`, or `No-show`.
- **BR31:** A doctor-created follow-up appointment must reference the preceding appointment through a recursive relationship.
- **BR32:** If a patient does not attend, the appointment status must be updated to `No-show`.
- **BR33:** Cancelled and No-show appointments remain recorded in appointment history.
- **BR34:** A doctor must not have overlapping active appointments.
- **BR35:** Cancelled and No-show appointments are not treated as active appointments for conflict checking.

## 1.2.6 Consultation Session

- **BR36:** Each consultation session must have a unique `SessionID`.
- **BR37:** A consultation session can only exist for a valid appointment.
- **BR38:** Each consultation session must be linked to exactly one appointment and must use the patient and doctor assigned to that appointment.
- **BR39:** Each session records exact start time, end time, and computed actual duration in minutes.
- **BR40:** Each session records clinical notes and whether it is `In-person` or `Virtual`.

## 1.2.7 Medical History

- **BR41:** A patient may accumulate multiple medical history records.
- **BR42:** Each medical history record belongs to one patient and is linked to the consultation session in which the diagnosis was established.
- **BR43:** A record contains diagnosis, symptoms, record date, and progress notes.
- **BR44:** Previous medical history records are permanent clinical archives and should not be deleted.

## 1.2.8 Prescription

- **BR45:** Each prescription must have a unique `PrescriptionID`.
- **BR46:** A prescription must be issued for a valid patient by a valid doctor and linked to a valid consultation session.
- **BR47:** The prescription doctor must be the attending doctor assigned to the related consultation and appointment.
- **BR48:** Each prescription must contain one or more `PRESCRIPTION_ITEM` records.

## 1.2.9 Medication and Prescription Item

- **BR49:** Each prescription item must reference a valid `MEDICATION` and define dosage, frequency, duration, and special instructions.

---

## 1.2.10 Main Constraints

### Cross-Entity, Workflow, and Telemedicine Rules

- **BR50:** `APPOINTMENT.DoctorID` must match the `DoctorID` of the selected `DOCTOR_SCHEDULE`.
- **BR51:** `AppointmentDateTime` must occur on the selected `ScheduleDate` and fall within its `StartTime-EndTime` interval.
- **BR52:** `MEDICAL_HISTORY` can only be created when the related `APPOINTMENT` has `Status = Completed`.
- **BR53:** `PRESCRIPTION` can only be created when the related `APPOINTMENT` has `Status = Completed`.
- **BR54:** `PRESCRIPTION.PatientID` must match the `PatientID` of the referenced `APPOINTMENT`.
- **BR55:** `PRESCRIPTION.DoctorID` must match the `DoctorID` of the referenced `APPOINTMENT`.
- **BR56:** The `CONSULTATION_SESSION` referenced by `PRESCRIPTION` or `MEDICAL_HISTORY` must belong to the same `APPOINTMENT` referenced by that clinical record.
- **BR57:** A telemedicine appointment must use a Virtual consultation session when the consultation is conducted remotely.
- **BR58:** A Virtual consultation session may store a meeting URL or virtual consultation reference required for remote patient-doctor interaction.

### Integrity Constraints

- **IC1 - Entity Integrity:** Every primary entity must have a unique, non-null primary key.
- **IC2 - Referential Integrity:** Every foreign key must reference an existing parent key.
- **IC3 - Domain Integrity:** Role, AppointmentType, Status, AvailabilityStatus, dates, and timestamps must conform to defined domains.
- **IC4 - Uniqueness Constraints:** Username, PatientID, DoctorID, and LicenseNumber must be unique where required.
- **IC5 - Specialization Integrity:** Every doctor belongs to exactly one of the two total and disjoint subtypes.
- **IC6 - Scheduling Integrity:** A doctor cannot have overlapping working schedules or overlapping active appointments.
- **IC7 - Workflow Integrity:** A consultation session cannot exist without a valid appointment; medical history and prescriptions require a completed appointment.
- **IC8 - Temporal Integrity:** AppointmentDateTime must match the selected schedule date and time interval; consultation start/end times must be logically ordered.
- **IC9 - Cross-Entity Consistency:** The appointment doctor must own the selected schedule.
- **IC10 - Clinical Record Consistency:** Prescription and medical history references must remain consistent with the same appointment and consultation session.
- **IC11 - Telemedicine Integrity:** When an appointment is conducted as Telemedicine, the corresponding consultation session must use `SessionType = Virtual`.

---

# 2. Database Design

*ISO/IEC 19505 / IE Standards*

## 2.1 Conceptual Model (ER/EER Diagram)

The conceptual model represents the main entities, attributes, relationships, cardinalities, and specialization required by the Healthcare Clinic & Telemedicine Portal.

---

## Entity Overview

| Entity | Primary Key | Purpose |
|---|---|---|
| `USER_ACCOUNT` | `UserID` | Stores user login credentials and role information for ADMIN, DOCTOR, and PATIENT users. |
| `PATIENT` | `PatientID` | Stores patient personal, contact, and basic healthcare information. |
| `DOCTOR` | `DoctorID` | Stores common personal and professional information of doctors. |
| `GENERAL_PRACTITIONER` | `DoctorID` | Represents General Practitioners as a subtype of DOCTOR. |
| `SPECIALIST` | `DoctorID` | Represents Specialist doctors and links them to a medical specialty. |
| `SPECIALTY` | `SpecialtyID` | Stores medical specialty information. |
| `DOCTOR_SCHEDULE` | `ScheduleID` | Stores doctors' available working schedules and time periods. |
| `APPOINTMENT` | `AppointmentID` | Stores appointments between patients and doctors, including appointment type, status, and follow-up information. |
| `CONSULTATION_SESSION` | `SessionID` | Stores actual consultation sessions created from valid appointments. |
| `MEDICAL_HISTORY` | `MedicalHistoryID` | Stores patients' diagnosis, symptoms, and progress notes from consultation sessions. |
| `PRESCRIPTION` | `PrescriptionID` | Stores digital prescriptions issued during consultation sessions. |
| `PRESCRIPTION_ITEM` | `PrescriptionItemID` | Connects prescriptions with medications and stores dosage, frequency, duration, and instructions. |
| `MEDICATION` | `MedicationID` | Stores medication information used in prescriptions. |

---

# USER_ACCOUNT and Role Structure

The system uses `USER_ACCOUNT` as the central entity for **Role-Based Access Control (RBAC)**.

Each account is assigned exactly one role:

- `ADMIN`
- `DOCTOR`
- `PATIENT`

## ADMIN

- Manage user accounts.
- Manage doctor information.
- Manage doctor schedules.
- Create appointments on behalf of patients.
- Adjust or cancel appointments.
- Manage administrative information.

> **Note:** No separate `ADMIN` entity is required because the administrative role is represented through the `Role` attribute of `USER_ACCOUNT`.

## DOCTOR

- Manage working schedules.
- View assigned appointments.
- Conduct consultation sessions.
- Record medical history.
- Issue prescriptions.
- Create follow-up appointments.

## PATIENT

- Manage personal information.
- Book appointments.
- View appointments.
- Participate in telemedicine consultations.
- View personal medical history.
- View prescriptions issued to them.

### Account Relationships

- `USER_ACCOUNT → DOCTOR`: `1 : 0..1`
- `USER_ACCOUNT → PATIENT`: `1 : 0..1`

Every `DOCTOR` and `PATIENT` profile must be associated with exactly one `USER_ACCOUNT`.

---

# Relationship Summary

| Relationship | Cardinality | Business Rule |
|---|---|---|
| `USER_ACCOUNT – PATIENT` | `1 : 0..1` | A user account may be associated with at most one Patient profile, and each Patient must have one User Account. |
| `USER_ACCOUNT – DOCTOR` | `1 : 0..1` | A user account may be associated with at most one Doctor profile, and each Doctor must have one User Account. |
| `PATIENT – APPOINTMENT` | `1 : N` | A Patient may book many Appointments, while each Appointment belongs to exactly one Patient. |
| `DOCTOR – APPOINTMENT` | `1 : N` | A Doctor may handle many Appointments, while each Appointment is assigned to exactly one Doctor. |
| `DOCTOR – DOCTOR_SCHEDULE` | `1 : N` | A Doctor may have many schedule records, while each Doctor Schedule belongs to one Doctor. |
| `DOCTOR_SCHEDULE – APPOINTMENT` | `1 : N` | One Doctor Schedule may be used for multiple Appointments, while each Appointment references one Doctor Schedule. |
| `DOCTOR – GENERAL_PRACTITIONER` | `1 : 0..1` | A Doctor may be classified as a General Practitioner. |
| `DOCTOR – SPECIALIST` | `1 : 0..1` | A Doctor may be classified as a Specialist. |
| `SPECIALTY – SPECIALIST` | `1 : N` | One Specialty may contain many Specialists, while each Specialist belongs to exactly one Specialty. |
| `APPOINTMENT – APPOINTMENT` | `1 : 0..N` | An Appointment may be the original appointment for one or more follow-up appointments. |
| `APPOINTMENT – CONSULTATION_SESSION` | `1 : 0..1` | An Appointment may result in at most one Consultation Session, and each Consultation Session belongs to one Appointment. |
| `APPOINTMENT – MEDICAL_HISTORY` | `1 : N` | An Appointment may be associated with multiple Medical History records. |
| `CONSULTATION_SESSION – MEDICAL_HISTORY` | `1 : N` | One Consultation Session may generate multiple Medical History records. |
| `CONSULTATION_SESSION – PRESCRIPTION` | `1 : N` | One Consultation Session may issue multiple Prescriptions. |
| `PATIENT – MEDICAL_HISTORY` | `1 : N` | A Patient may have many Medical History records, while each record belongs to one Patient. |
| `PATIENT – PRESCRIPTION` | `1 : N` | A Patient may receive many Prescriptions, while each Prescription belongs to one Patient. |
| `DOCTOR – PRESCRIPTION` | `1 : N` | A Doctor may issue many Prescriptions, while each Prescription is issued by one Doctor. |
| `PRESCRIPTION – PRESCRIPTION_ITEM` | `1 : N` | One Prescription contains one or more Prescription Items. |
| `MEDICATION – PRESCRIPTION_ITEM` | `1 : N` | One Medication may appear in many Prescription Items, while each Prescription Item references one Medication. |

---

# EER Specialization

`DOCTOR` is specialized into two subtypes:

- `GENERAL_PRACTITIONER`
- `SPECIALIST`

`SPECIALIST` is associated with `SPECIALTY`.

The specialization is **Total and Disjoint**.

### Total Specialization

Every `DOCTOR` must belong to one subtype.

### Disjoint Specialization

A doctor cannot simultaneously be both:

- `GENERAL_PRACTITIONER`
- `SPECIALIST`

---

# Conceptual ER/EER Diagram

The ER/EER Diagram should include:

- All entities listed above
- Primary and foreign keys
- Relationship cardinalities
- Recursive relationship of `APPOINTMENT`
- `DOCTOR` specialization
- `GENERAL_PRACTITIONER`
- `SPECIALIST`
- `SPECIALTY`
- Total specialization
- Disjoint constraint
