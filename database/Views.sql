
USE Phrase3;

-- VIEW 1: Appointment Details

CREATE OR REPLACE VIEW vw_AppointmentDetails AS
SELECT
    a.AppointmentID,
    p.FullName AS PatientName,
    d.FullName AS DoctorName,
    a.AppointmentDateTime,
    a.EstimatedDuration,
    a.Modality,
    a.Status
FROM APPOINTMENT a
INNER JOIN PATIENT p
    ON a.Patient = p.Patient
INNER JOIN DOCTOR d
    ON a.DoctorID = d.DoctorID;


-- VIEW 2: Prescription Details
-- Display patient prescriptions and medications

CREATE OR REPLACE VIEW vw_PrescriptionDetails AS
SELECT
    pr.PrescriptionID,
    p.FullName AS PatientName,
    d.FullName AS DoctorName,
    pr.IssueDate,
    m.MedicationName,
    pi.Dosage,
    pi.Frequency,
    pi.Duration,
    pi.SpecialInstructions
FROM PRESCRIPTION pr
INNER JOIN PATIENT p
    ON pr.Patient = p.Patient
INNER JOIN DOCTOR d
    ON pr.DoctorID = d.DoctorID
INNER JOIN PRESCRIPTION_ITEM pi
    ON pr.PrescriptionID = pi.PrescriptionID
INNER JOIN MEDICATION m
    ON pi.MedicationID = m.MedicationID;
