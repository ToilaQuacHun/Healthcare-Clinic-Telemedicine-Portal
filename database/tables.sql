-- MySQL dump 10.13  Distrib 8.0.46, for macos15 (arm64)
--
-- Host: localhost    Database: Phrase3
-- ------------------------------------------------------
-- Server version	8.4.11

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `APPOINTMENT`
--

DROP TABLE IF EXISTS `APPOINTMENT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `APPOINTMENT` (
  `AppointmentID` int NOT NULL,
  `Patient` int NOT NULL,
  `DoctorID` int NOT NULL,
  `ScheduleID` int NOT NULL,
  `PrecedingAppointmentID` int DEFAULT NULL,
  `AppointmentDateTime` datetime NOT NULL,
  `EstimatedDuration` int NOT NULL,
  `Modality` varchar(20) DEFAULT NULL,
  `Status` varchar(20) DEFAULT 'Scheduled',
  `CreatedBy` varchar(50) NOT NULL,
  PRIMARY KEY (`AppointmentID`),
  KEY `Patient` (`Patient`),
  KEY `DoctorID` (`DoctorID`),
  KEY `ScheduleID` (`ScheduleID`),
  KEY `PrecedingAppointmentID` (`PrecedingAppointmentID`),
  CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`Patient`) REFERENCES `PATIENT` (`Patient`),
  CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`DoctorID`) REFERENCES `DOCTOR` (`DoctorID`),
  CONSTRAINT `appointment_ibfk_3` FOREIGN KEY (`ScheduleID`) REFERENCES `DOCTOR_SCHEDULE` (`ScheduleID`),
  CONSTRAINT `appointment_ibfk_4` FOREIGN KEY (`PrecedingAppointmentID`) REFERENCES `APPOINTMENT` (`AppointmentID`),
  CONSTRAINT `appointment_chk_1` CHECK ((`Modality` in (_utf8mb4'In-person',_utf8mb4'Telemedicine'))),
  CONSTRAINT `appointment_chk_2` CHECK ((`Status` in (_utf8mb4'Scheduled',_utf8mb4'Checked-In',_utf8mb4'Completed',_utf8mb4'Cancelled',_utf8mb4'No-show')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `CONSULTATION_SESSION`
--

DROP TABLE IF EXISTS `CONSULTATION_SESSION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CONSULTATION_SESSION` (
  `SessionID` int NOT NULL,
  `AppointmentID` int NOT NULL,
  `StartTime` datetime NOT NULL,
  `EndTime` datetime NOT NULL,
  `ActualDuration` int NOT NULL,
  `SessionType` varchar(20) DEFAULT NULL,
  `ClinicalNotes` text,
  `MeetingURL` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`SessionID`),
  UNIQUE KEY `AppointmentID` (`AppointmentID`),
  CONSTRAINT `consultation_session_ibfk_1` FOREIGN KEY (`AppointmentID`) REFERENCES `APPOINTMENT` (`AppointmentID`),
  CONSTRAINT `consultation_session_chk_1` CHECK ((`SessionType` in (_utf8mb4'In-person',_utf8mb4'Virtual')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DOCTOR`
--

DROP TABLE IF EXISTS `DOCTOR`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DOCTOR` (
  `DoctorID` int NOT NULL,
  `UserID` int DEFAULT NULL,
  `FullName` varchar(100) NOT NULL,
  `ContactInfo` varchar(50) DEFAULT NULL,
  `LicenseNumber` varchar(50) NOT NULL,
  PRIMARY KEY (`DoctorID`),
  UNIQUE KEY `LicenseNumber` (`LicenseNumber`),
  UNIQUE KEY `UserID` (`UserID`),
  CONSTRAINT `doctor_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `USER_ACCOUNT` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `DOCTOR_SCHEDULE`
--

DROP TABLE IF EXISTS `DOCTOR_SCHEDULE`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DOCTOR_SCHEDULE` (
  `ScheduleID` int NOT NULL,
  `DoctorID` int NOT NULL,
  `ScheduleDate` date NOT NULL,
  `StartTime` time NOT NULL,
  `EndTime` time NOT NULL,
  `AvailabilityStatus` varchar(20) NOT NULL,
  PRIMARY KEY (`ScheduleID`),
  KEY `DoctorID` (`DoctorID`),
  CONSTRAINT `doctor_schedule_ibfk_1` FOREIGN KEY (`DoctorID`) REFERENCES `DOCTOR` (`DoctorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `GENERAL_PRACTITIONED`
--

DROP TABLE IF EXISTS `GENERAL_PRACTITIONED`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `GENERAL_PRACTITIONED` (
  `DoctorID` int NOT NULL,
  PRIMARY KEY (`DoctorID`),
  CONSTRAINT `general_practitioned_ibfk_1` FOREIGN KEY (`DoctorID`) REFERENCES `DOCTOR` (`DoctorID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MEDICAL_HISTORY`
--

DROP TABLE IF EXISTS `MEDICAL_HISTORY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MEDICAL_HISTORY` (
  `MedicalHistoryID` int NOT NULL,
  `Patient` int NOT NULL,
  `SessionID` int NOT NULL,
  `Diagnosis` text NOT NULL,
  `Symptoms` text,
  `RecordDate` date NOT NULL,
  `ProgressNotes` text,
  PRIMARY KEY (`MedicalHistoryID`),
  KEY `Patient` (`Patient`),
  KEY `SessionID` (`SessionID`),
  CONSTRAINT `medical_history_ibfk_1` FOREIGN KEY (`Patient`) REFERENCES `PATIENT` (`Patient`),
  CONSTRAINT `medical_history_ibfk_2` FOREIGN KEY (`SessionID`) REFERENCES `CONSULTATION_SESSION` (`SessionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MEDICATION`
--

DROP TABLE IF EXISTS `MEDICATION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MEDICATION` (
  `MedicationID` int NOT NULL,
  `MedicationName` varchar(100) NOT NULL,
  `Description` text,
  PRIMARY KEY (`MedicationID`),
  UNIQUE KEY `MedicationName` (`MedicationName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PATIENT`
--

DROP TABLE IF EXISTS `PATIENT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PATIENT` (
  `Patient` int NOT NULL,
  `UserID` int DEFAULT NULL,
  `FullName` varchar(100) NOT NULL,
  `BloodType` varchar(5) DEFAULT NULL,
  `Allergies` text,
  `ChronicDiseases` text,
  `EmergencyContact` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`Patient`),
  UNIQUE KEY `UserID` (`UserID`),
  CONSTRAINT `patient_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `USER_ACCOUNT` (`UserID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PRESCRIPTION`
--

DROP TABLE IF EXISTS `PRESCRIPTION`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PRESCRIPTION` (
  `PrescriptionID` int NOT NULL,
  `Patient` int NOT NULL,
  `DoctorID` int NOT NULL,
  `SessionID` int NOT NULL,
  `IssueDate` date NOT NULL,
  PRIMARY KEY (`PrescriptionID`),
  KEY `Patient` (`Patient`),
  KEY `DoctorID` (`DoctorID`),
  KEY `SessionID` (`SessionID`),
  CONSTRAINT `prescription_ibfk_1` FOREIGN KEY (`Patient`) REFERENCES `PATIENT` (`Patient`),
  CONSTRAINT `prescription_ibfk_2` FOREIGN KEY (`DoctorID`) REFERENCES `DOCTOR` (`DoctorID`),
  CONSTRAINT `prescription_ibfk_3` FOREIGN KEY (`SessionID`) REFERENCES `CONSULTATION_SESSION` (`SessionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PRESCRIPTION_ITEM`
--

DROP TABLE IF EXISTS `PRESCRIPTION_ITEM`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PRESCRIPTION_ITEM` (
  `PrescriptionItemID` int NOT NULL,
  `PrescriptionID` int NOT NULL,
  `MedicationID` int NOT NULL,
  `Dosage` varchar(50) NOT NULL,
  `Frequency` varchar(50) NOT NULL,
  `Duration` varchar(50) NOT NULL,
  `SpecialInstructions` text,
  PRIMARY KEY (`PrescriptionItemID`),
  KEY `PrescriptionID` (`PrescriptionID`),
  KEY `MedicationID` (`MedicationID`),
  CONSTRAINT `prescription_item_ibfk_1` FOREIGN KEY (`PrescriptionID`) REFERENCES `PRESCRIPTION` (`PrescriptionID`),
  CONSTRAINT `prescription_item_ibfk_2` FOREIGN KEY (`MedicationID`) REFERENCES `MEDICATION` (`MedicationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SPECIALIST`
--

DROP TABLE IF EXISTS `SPECIALIST`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SPECIALIST` (
  `DoctorID` int NOT NULL,
  `SpecialtyID` int NOT NULL,
  PRIMARY KEY (`DoctorID`),
  KEY `SpecialtyID` (`SpecialtyID`),
  CONSTRAINT `specialist_ibfk_1` FOREIGN KEY (`DoctorID`) REFERENCES `Doctor` (`DoctorID`),
  CONSTRAINT `specialist_ibfk_2` FOREIGN KEY (`SpecialtyID`) REFERENCES `Specialty` (`SpecialtyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `SPECIALTY`
--

DROP TABLE IF EXISTS `SPECIALTY`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `SPECIALTY` (
  `SpecialtyID` int NOT NULL,
  `SpecialtyName` varchar(100) NOT NULL,
  PRIMARY KEY (`SpecialtyID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `USER_ACCOUNT`
--

DROP TABLE IF EXISTS `USER_ACCOUNT`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `USER_ACCOUNT` (
  `UserID` int NOT NULL,
  `Username` varchar(50) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `Role` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `Username` (`Username`),
  CONSTRAINT `user_account_chk_1` CHECK ((`Role` in (_utf8mb4'ADMIN',_utf8mb4'DOCTOR',_utf8mb4'PATIENT')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-08  8:35:36
