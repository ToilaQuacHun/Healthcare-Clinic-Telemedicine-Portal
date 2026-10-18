
-- QUERY 1: Patient Appointment Details
-- Display appointments with patient and doctor information

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
    ON a.DoctorID = d.DoctorID
ORDER BY a.AppointmentDateTime DESC;


-- QUERY 2: Doctor Schedule Overview
-- Display doctor schedules and number of appointments

SELECT
    d.DoctorID,
    d.FullName AS DoctorName,
    ds.ScheduleDate,
    ds.StartTime,
    ds.EndTime,
    ds.AvailabilityStatus,
    COUNT(a.AppointmentID) AS TotalAppointments
FROM DOCTOR d
INNER JOIN DOCTOR_SCHEDULE ds
    ON d.DoctorID = ds.DoctorID
LEFT JOIN APPOINTMENT a
    ON ds.ScheduleID = a.ScheduleID
GROUP BY
    d.DoctorID,
    d.FullName,
    ds.ScheduleID,
    ds.ScheduleDate,
    ds.StartTime,
    ds.EndTime,
    ds.AvailabilityStatus
ORDER BY ds.ScheduleDate ASC, ds.StartTime ASC;


-- QUERY 3: Patient Medical History
-- Display patients' medical histories
-- with consultation and doctor information

SELECT
    mh.MedicalHistoryID,
    p.Patient AS PatientID,
    p.FullName AS PatientName,
    d.FullName AS DoctorName,
    mh.RecordDate,
    mh.Symptoms,
    mh.Diagnosis,
    mh.ProgressNotes,
    cs.SessionType,
    cs.ActualDuration
FROM MEDICAL_HISTORY mh
INNER JOIN PATIENT p
    ON mh.Patient = p.Patient
INNER JOIN CONSULTATION_SESSION cs
    ON mh.SessionID = cs.SessionID
INNER JOIN APPOINTMENT a
    ON cs.AppointmentID = a.AppointmentID
INNER JOIN DOCTOR d
    ON a.DoctorID = d.DoctorID
ORDER BY
    mh.RecordDate DESC,
    p.FullName ASC;

-- QUERY 4: Prescription Details
-- Display prescriptions with medication details

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
    ON pi.MedicationID = m.MedicationID
ORDER BY pr.IssueDate DESC,
         pr.PrescriptionID;
         

-- QUERY 5: Appointments per Doctor
-- Count appointments for each doctor

SELECT
    d.DoctorID,
    d.FullName AS DoctorName,
    COUNT(a.AppointmentID) AS TotalAppointments
FROM DOCTOR d
LEFT JOIN APPOINTMENT a
    ON d.DoctorID = a.DoctorID
GROUP BY
    d.DoctorID,
    d.FullName
ORDER BY TotalAppointments DESC;

-- QUERY 6: Frequent Patients
-- Find patients with more than 3 appointments

SELECT
    p.Patient AS PatientID,
    p.FullName AS PatientName,
    COUNT(a.AppointmentID) AS TotalAppointments
FROM PATIENT p
INNER JOIN APPOINTMENT a
    ON p.Patient = a.Patient
GROUP BY
    p.Patient,
    p.FullName
HAVING COUNT(a.AppointmentID) > 3
ORDER BY TotalAppointments DESC;



-- QUERY 7: Patients Without Appointments
-- Find patients who have never booked an appointment

SELECT
    p.Patient AS PatientID,
    p.FullName AS PatientName,
    p.BloodType,
    p.EmergencyContact
FROM PATIENT p
WHERE NOT EXISTS (
    SELECT 1
    FROM APPOINTMENT a
    WHERE a.Patient = p.Patient
)
ORDER BY p.FullName;


-- QUERY 8: Above-Average Doctor Workload
-- Find doctors with above-average appointments

WITH DoctorWorkload AS (
    SELECT
        d.DoctorID,
        d.FullName AS DoctorName,
        COUNT(a.AppointmentID) AS TotalAppointments
    FROM DOCTOR d
    LEFT JOIN APPOINTMENT a
        ON d.DoctorID = a.DoctorID
    GROUP BY d.DoctorID, d.FullName
)
SELECT
    DoctorID,
    DoctorName,
    TotalAppointments
FROM DoctorWorkload
WHERE TotalAppointments > (
    SELECT AVG(TotalAppointments)
    FROM DoctorWorkload
)
ORDER BY TotalAppointments DESC;


-- QUERY 9: Telemedicine Statistics
-- Count telemedicine appointments by month

SELECT
    YEAR(a.AppointmentDateTime) AS AppointmentYear,
    MONTH(a.AppointmentDateTime) AS AppointmentMonth,
    COUNT(DISTINCT a.AppointmentID) AS TotalTelemedicine
FROM APPOINTMENT a
INNER JOIN CONSULTATION_SESSION cs
    ON a.AppointmentID = cs.AppointmentID
WHERE a.Modality = 'Telemedicine'
  AND cs.SessionType = 'Virtual'
GROUP BY
    YEAR(a.AppointmentDateTime),
    MONTH(a.AppointmentDateTime)
ORDER BY AppointmentYear,
         AppointmentMonth;
         

-- QUERY 10: Doctor Specialization Statistics
-- Count appointments by doctor classification

WITH DoctorTypes AS (
    SELECT
        d.DoctorID,
        CASE
            WHEN gp.DoctorID IS NOT NULL
                 AND sp.DoctorID IS NULL
                THEN 'General Practitioner'
            WHEN sp.DoctorID IS NOT NULL
                 AND gp.DoctorID IS NULL
                THEN 'Specialist'
            WHEN gp.DoctorID IS NOT NULL
                 AND sp.DoctorID IS NOT NULL
                THEN 'Both Types'
            ELSE 'Unclassified'
        END AS DoctorType
    FROM DOCTOR d
    LEFT JOIN GENERAL_PRACTITIONED gp
        ON d.DoctorID = gp.DoctorID
    LEFT JOIN SPECIALIST sp
        ON d.DoctorID = sp.DoctorID
)
SELECT
    dt.DoctorType,
    COUNT(DISTINCT dt.DoctorID) AS TotalDoctors,
    COUNT(a.AppointmentID) AS TotalAppointments
FROM DoctorTypes dt
LEFT JOIN APPOINTMENT a
    ON dt.DoctorID = a.DoctorID
GROUP BY dt.DoctorType
ORDER BY TotalAppointments DESC;