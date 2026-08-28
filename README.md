# Database Project Report Template
Project ID & Title: (Healthcare Clinic & Telemedicine Portal)
## A. Project Identity
Team Name: G2

Team Members:

Lê Nguyễn Quốc Hùng n24dece070@student.ptithcm.edu.vn

Trần Hoàng Hải Đăng n24dece059@student.ptithcm.edu.vn

Trần Quốc Huy n24dece074@student.ptithcm.edu.vn

Project Title: 
MediConnect: Integrated Healthcare Clinic & Telemedicine Management System
## B. Report structure

### 1.Introduction & Project Scope (Adapted from ISO/IEC/IEEE 29148)
Healthcare clinics need to manage a large amount of information every day, including patient information, doctor information, appointments, doctor schedules, medical histories, and prescriptions. If this information is stored separately or managed manually, it may lead to duplicated records, appointment conflicts, missing patient history, or difficulties in tracking prescriptions.

In addition, healthcare services today may be provided in two forms: traditional in-person consultation and telemedicine consultation. Therefore, clinics need a structured database that can manage both types of appointments while keeping patient and doctor information consistent.

The Healthcare Clinic & Telemedicine Portal is designed as a centralized database system to support the basic operations of a clinic. The system focuses on managing patients, doctors, doctor schedules, appointments, medical histories, prescriptions, and medications. It also supports the classification of doctors into General Practitioners and Specialists.

#### 1.1System Objective
The main objective of the system is to provide a reliable database for storing and managing the essential information of a healthcare clinic.

The system is designed to:
- Store and manage patient information.
- Store and manage doctor information.
- Classify doctors as General Practitioners or Specialists.
- Store medical specialty information for Specialists.
- Manage doctor schedules and available working periods.
- Manage appointments between Patients and Doctors.
- Support two appointment types: In-person and Telemedicine.
- Maintain patient medical history.
- Store digital prescriptions issued by Doctors.
- Store medication information used in prescriptions.
- Maintain the relationship between prescriptions and medications.
The database aims to improve data consistency and make it easier to retrieve related healthcare information.
#### 1.2Business Rules & Constraints
##### 1.2.1 Patient
- BR1: Each Patient must have a unique PatientID.
- BR2: A Patient may have many Appointments.
- BR3: Each Appointment must belong to exactly one Patient.
- BR4: A Patient may have many Medical History records.
- BR5: Each Medical History record must belong to exactly one Patient.
##### 1.2.2 Doctor and Medical Staff
- BR6: Each Doctor must have a unique DoctorID.
- BR7: Each Doctor may be classified as either a General Practitioner or a Specialist.
- BR8: Each General Practitioner must reference an existing Doctor.
- BR9: Each Specialist must reference an existing Doctor.
- BR10: Each Specialist must belong to exactly one Specialty.
- BR11: One Specialty may be associated with many Specialists.
##### 1.2.3 Doctor Schedule
- BR12: A Doctor may have many Doctor Schedule records.
- BR13: Each Doctor Schedule must belong to exactly one Doctor.
- BR14: Each Doctor Schedule contains a schedule date, start time, and end time.
##### 1.2.4 Appointment
- BR15: A Patient may book many Appointments.
- BR16: A Doctor may handle many Appointments.
- BR17: Each Appointment must be associated with exactly one Patient.
- BR18: Each Appointment must be associated with exactly one Doctor.
- BR19: Each Appointment must reference one Doctor Schedule.
- BR20: Each Appointment must contain an appointment date and time.
- BR21: Each Appointment must have an AppointmentType.
- BR22: AppointmentType must represent either In-person or Telemedicine.
- BR23: Each Appointment must have a status.
##### 1.2.5 Medical History
- BR24: A Patient may have many Medical History records.
- BR25: Each Medical History record must belong to one Patient.
- BR26: A Medical History record may contain diagnosis, symptoms, and notes.
##### 1.2.6 Prescription
- BR27: Each Prescription must belong to exactly one Patient.
- BR28: Each Prescription must be issued by exactly one Doctor.
- BR29: Each Prescription must be associated with exactly one Appointment.
- BR30: One Appointment can have at most one Prescription.
- BR31: A Patient may have many Prescriptions.
- BR32: A Doctor may issue many Prescriptions.
##### 1.2.7 Medication and Prescription Item
- BR33: Each Medication must have a unique MedicationID.
- BR34: A Prescription may contain multiple Medications.
- BR35: A Medication may appear in multiple Prescriptions.
- BR36: The many-to-many relationship between Prescription and Medication is resolved through PRESCRIPTION_ITEM.
- BR37: Each Prescription Item references one Prescription and one Medication.
- BR38: A Prescription Item may store dosage, frequency, duration, and specific instructions.
##### 1.2.8 Main Constraints
The database design applies the following major constraints:

PatientID must be unique.

DoctorID must be unique.

LicenseNumber must be unique for Doctors when provided.

Specialist.DoctorID must reference an existing Doctor.

General_Practitioner.DoctorID must reference an existing Doctor.

Specialist.SpecialtyID must reference an existing Specialty.

Doctor_Schedule.DoctorID must reference an existing Doctor.

Appointment.PatientID must reference an existing Patient.

Appointment.DoctorID must reference an existing Doctor.

Appointment.ScheduleID must reference an existing Doctor Schedule.

Medical_History.PatientID must reference an existing Patient.

Prescription.PatientID must reference an existing Patient.

Prescription.DoctorID must reference an existing Doctor.

Prescription.AppointmentID must reference an existing Appointment.

Each Appointment can have at most one Prescription because AppointmentID is unique in the Prescription table.

Prescription_Item must reference an existing Prescription and Medication.

### 2.Database Design (ISO/IEC 19505 / IE Standards)

#### 2.1Conceptual Model (ER/EER Diagram)
##### Entity Overview

| Entity | Primary Key (PK) | Purpose |
|---|---|---|
| PATIENT | `PatientID` | Stores patient information. |
| DOCTOR | `DoctorID` | Stores common information about doctors. |
| GENERAL_PRACTITIONER | `DoctorID` (FK) | Represents General Practitioners as a subtype of Doctor. |
| SPECIALIST | `DoctorID` (FK) | Represents Specialists as a subtype of Doctor. |
| SPECIALTY | `SpecialtyID` | Stores medical specialty information. |
| DOCTOR_SCHEDULE | `ScheduleID` | Stores doctor schedules and availability. |
| APPOINTMENT | `AppointmentID` | Stores appointments between patients and doctors. |
| MEDICAL_HISTORY | `MedicalHistoryID` | Stores patient medical history records. |
| PRESCRIPTION | `PrescriptionID` | Stores digital prescriptions issued by doctors. |
| MEDICATION | `MedicationID` | Stores medication information. |
| PRESCRIPTION_ITEM | `PrescriptionID`, `MedicationID` | Connects prescriptions and medications and stores dosage details. |
