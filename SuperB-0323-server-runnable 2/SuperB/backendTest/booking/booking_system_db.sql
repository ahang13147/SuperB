-- @version: 3/3/2025
-- @author: Xin Yu, Siyan Guo, Zibang Nie
-- @description: This SQL script creates a booking system database, which includes tables for Users, Rooms, Bookings, Approvals, Notifications, and Reports.
-- It provides a structure to manage users, room bookings, approval processes, notifications, and report generation.

-- Set session variables for compatibility
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Drop the existing database if it exists and create a new one
DROP DATABASE IF EXISTS `booking_system_db`;
CREATE DATABASE `booking_system_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `booking_system_db`;

-- 1.1 Users Table (Stores user information)
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,    -- User ID, auto-incremented
    username VARCHAR(255) NOT NULL,             -- Username
    email VARCHAR(255) NOT NULL UNIQUE,         -- User's email, must be unique
    password_hash VARCHAR(255) NOT NULL,        -- Hashed password for security
    role ENUM('admin', 'professor', 'student', 'tutor') NOT NULL  -- User's role in the system
    -- Additional fields (e.g., phone number) can be added here if needed
);

-- 1.2 Rooms Table (Stores room details)
CREATE TABLE Rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,    -- Room ID, auto-incremented
    room_name VARCHAR(255) NOT NULL,            -- Room name
    capacity INT NOT NULL,                      -- Room capacity
    equipment TEXT,                             -- Equipment available in the room
    location VARCHAR(255),                      -- Room's physical location
    availability BOOLEAN DEFAULT TRUE          -- Availability status of the room
);

-- 1.3 Room Availability Table (Stores room availability information for specific times)
CREATE TABLE Room_availability (
    availability_id INT PRIMARY KEY,           -- Availability ID, primary key
    room_id INT,                               -- Foreign key referencing the Rooms table
    available_begin TIME,                      -- Start time of room availability
    available_end TIME,                        -- End time of room availability
    available_date DATE,                       -- Date of room availability
    is_available BOOLEAN,                      -- Whether the room is available
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id) -- Foreign key constraint referencing the Rooms table
);

-- 1.4 Bookings Table (Stores booking information for each booking request)
CREATE TABLE Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,  -- Booking ID, auto-incremented
    user_id INT NOT NULL,                       -- User ID (Foreign key referencing Users table)
    room_id INT NOT NULL,                       -- Room ID (Foreign key referencing Rooms table)
    start_time TIME NOT NULL,               -- Start time of the booking
    end_time TIME NOT NULL,
    start_date DATE,-- End time of the booking
    status ENUM('pending', 'approved', 'canceled', 'rejected') NOT NULL,  -- Booking status

    FOREIGN KEY (user_id) REFERENCES Users(user_id),  -- Foreign key referencing Users table
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)   -- Foreign key referencing Rooms table
);

-- 1.5 Approvals Table (Stores approval statuses for each booking)
CREATE TABLE Approvals (
    approval_id INT AUTO_INCREMENT PRIMARY KEY,  -- Approval ID, auto-incremented
    booking_id INT NOT NULL,                     -- Booking ID (Foreign key referencing Bookings table)
    admin_id INT NOT NULL,                       -- Admin ID (Foreign key referencing Users table)
    approval_status ENUM('approved', 'rejected') NOT NULL,  -- Approval status
    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of approval
    FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id),  -- Foreign key referencing Bookings table
    FOREIGN KEY (admin_id) REFERENCES Users(user_id)  -- Foreign key referencing Users table (Admin)
);

-- 1.6 Notifications Table (Stores notifications for users regarding bookings)
CREATE TABLE Notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,  -- Notification ID, auto-incremented
    user_id INT NOT NULL,                            -- User ID (Foreign key referencing Users table)
    message TEXT NOT NULL,                           -- Notification message
    notification_type ENUM('confirmation', 'reminder', 'cancellation') NOT NULL,  -- Type of notification
    status ENUM('read', 'unread') DEFAULT 'unread',  -- Status of the notification (read/unread)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of notification creation
    FOREIGN KEY (user_id) REFERENCES Users(user_id)  -- Foreign key referencing Users table
);

-- 1.7 Reports Table (Stores reports generated by the admin)
CREATE TABLE Reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,      -- Report ID, auto-incremented
    admin_id INT NOT NULL,                          -- Admin ID (Foreign key referencing Users table)
    report_type ENUM('PDF', 'Excel') NOT NULL,      -- Type of report (PDF or Excel)
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp when the report is generated
    data JSON,                                     -- Report data stored in JSON format
    FOREIGN KEY (admin_id) REFERENCES Users(user_id)  -- Foreign key referencing Users table (Admin)
);

-- Create indexes to optimize query performance (optional)
CREATE INDEX idx_booking_user ON Bookings(user_id);  -- Index on user_id in Bookings table
CREATE INDEX idx_booking_room ON Bookings(room_id);  -- Index on room_id in Bookings table
CREATE INDEX idx_approval_booking ON Approvals(booking_id);  -- Index on booking_id in Approvals table
CREATE INDEX idx_approval_admin ON Approvals(admin_id);  -- Index on admin_id in Approvals table
CREATE INDEX idx_notification_user ON Notifications(user_id);  -- Index on user_id in Notifications table
CREATE INDEX idx_report_admin ON Reports(admin_id);  -- Index on admin_id in Reports table
