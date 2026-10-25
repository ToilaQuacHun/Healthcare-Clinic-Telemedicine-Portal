
USE Phrase3;

-- TRIGGER 1
-- BR34: Prevent overlapping appointments
-- BR35: Ignore Cancelled and No-show

DELIMITER $$

CREATE TRIGGER trg_prevent_overlap
BEFORE INSERT ON APPOINTMENT
FOR EACH ROW
BEGIN

    -- Check that duration is positive
    IF NEW.EstimatedDuration <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid appointment duration';
    END IF;

    -- Check for overlapping appointments
    IF NEW.Status NOT IN ('Cancelled', 'No-show')
       AND EXISTS (
           SELECT 1
           FROM APPOINTMENT a
           WHERE a.DoctorID = NEW.DoctorID

             AND a.Status NOT IN ('Cancelled', 'No-show')

             AND NEW.AppointmentDateTime <
                 DATE_ADD(
                     a.AppointmentDateTime,
                     INTERVAL a.EstimatedDuration MINUTE
                 )

             AND DATE_ADD(
                     NEW.AppointmentDateTime,
                     INTERVAL NEW.EstimatedDuration MINUTE
                 ) > a.AppointmentDateTime
       )
    THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Doctor has overlapping appointment';
    END IF;

END$$

DELIMITER ;






