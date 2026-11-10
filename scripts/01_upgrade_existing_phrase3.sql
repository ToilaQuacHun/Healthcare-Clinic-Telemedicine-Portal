-- Chay 1 lan tren BAN SAO database sau khi sao luu Phrase3.
-- Them trang thai IsActive cho xoa mem bac si, KHONG xoa/sua du lieu cu.
USE Phrase3;
DELIMITER $$
DROP PROCEDURE IF EXISTS mc4_upgrade_doctor_status$$
CREATE PROCEDURE mc4_upgrade_doctor_status()
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'DOCTOR'
          AND COLUMN_NAME = 'IsActive'
    ) THEN
        ALTER TABLE DOCTOR ADD COLUMN IsActive TINYINT(1) NOT NULL DEFAULT 1;
    END IF;
END$$
DELIMITER ;
CALL mc4_upgrade_doctor_status();
DROP PROCEDURE mc4_upgrade_doctor_status;
SELECT COUNT(*) AS TotalDoctors, SUM(IsActive=1) AS ActiveDoctors FROM DOCTOR;
