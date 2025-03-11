-- @version: 3/11/2025
-- @author: Xin Yu, Siyan Guo, Zibang Nie
-- @description: This SQL script creates a booking system database, which includes tables for Users, Rooms, Bookings, Approvals, Notifications, and Reports.
-- It provides a structure to manage users, room bookings, approval processes, notifications, and report generation.
-- ADD: add new tables of blacklist and trusted staff


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
);

-- 1.2 Rooms Table (Stores room details)
CREATE TABLE Rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,    -- Room ID, auto-incremented
    room_name VARCHAR(255) NOT NULL,            -- Room name
    capacity INT NOT NULL,                      -- Room capacity
    equipment TEXT,                             -- Equipment available in the room
    location VARCHAR(255)                       -- Room's physical location
);

-- 1.3 Room Availability Table (Stores room availability information for specific times)
CREATE TABLE Room_availability (
    availability_id INT AUTO_INCREMENT PRIMARY KEY,           -- Availability ID, primary key
    room_id INT,                               -- Foreign key referencing the Rooms table
    available_begin TIME,                      -- Start time of room availability
    available_end TIME,                        -- End time of room availability
    available_date DATE,                       -- Date of room availability
    availability INT,                          -- Whether the room is available      0: available   1: not available    2: booked
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id) -- Foreign key constraint referencing the Rooms table
);

-- 1.4 Bookings Table (Stores booking information for each booking request)
CREATE TABLE Bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,  -- Booking ID, auto-incremented
    user_id INT NOT NULL,                       -- User ID (Foreign key referencing Users table)
    room_id INT NOT NULL,                       -- Room ID (Foreign key referencing Rooms table)
    start_time TIME NOT NULL,                   -- Start time of the booking
    end_time TIME NOT NULL,
    booking_date DATE,                          -- End time of the booking
    status ENUM('pending', 'approved', 'canceled', 'rejected','failed') NOT NULL,  -- Booking status
	reason TEXT,

    FOREIGN KEY (user_id) REFERENCES Users(user_id),  -- Foreign key referencing Users table
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id)   -- Foreign key referencing Rooms table
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

-- 1.10 Room Trusted Users Table (Stores which users are trusted to book specific rooms)
CREATE TABLE RoomTrustedUsers (
    room_trusted_user_id INT AUTO_INCREMENT PRIMARY KEY,  -- Room Trusted User ID, auto-incremented
    room_id INT NOT NULL,                                 -- Room ID (Foreign key referencing Rooms table)
    user_id INT NOT NULL,                                 -- User ID (Foreign key referencing Users table)
    added_by INT NOT NULL,                                -- Admin ID who added this user to the trusted list
    added_date DATE,                                      -- Date when the user was added to the trusted list
    added_time TIME,                                      -- Time when the user was added to the trusted list
    notes TEXT,                                           -- Additional notes or reasons for adding this user
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id),      -- Foreign key referencing Rooms table
    FOREIGN KEY (user_id) REFERENCES Users(user_id),      -- Foreign key referencing Users table
    FOREIGN KEY (added_by) REFERENCES Users(user_id)      -- Foreign key referencing Users table (Admin)
);

-- 1.11 Blacklist Table (Stores users who are banned or restricted from using the system)
CREATE TABLE Blacklist (
    blacklist_id INT AUTO_INCREMENT PRIMARY KEY,    -- Blacklist ID, auto-incremented
    user_id INT NOT NULL,                           -- User ID (Foreign key referencing Users table)
    added_by INT NOT NULL,                          -- Admin ID who added this user to the blacklist
    added_date DATE,                                -- Date when the user was added to the blacklist
    added_time TIME,                                -- Time when the user was added to the blacklist
    start_date DATE NOT NULL,                       -- Start date of the blacklist period
    start_time TIME NOT NULL,                       -- Start time of the blacklist period
    end_date DATE NOT NULL,                         -- End date of the blacklist period
    end_time TIME NOT NULL,                         -- End time of the blacklist period
    reason TEXT,                                    -- Reason for adding this user to the blacklist
    FOREIGN KEY (user_id) REFERENCES Users(user_id),  -- Foreign key referencing Users table
    FOREIGN KEY (added_by) REFERENCES Users(user_id)  -- Foreign key referencing Users table (Admin)
);


-- Create indexes to optimize query performance (optional)
CREATE INDEX idx_booking_user ON Bookings(user_id);  -- Index on user_id in Bookings table
CREATE INDEX idx_booking_room ON Bookings(room_id);  -- Index on room_id in Bookings table
CREATE INDEX idx_notification_user ON Notifications(user_id);  -- Index on user_id in Notifications table
CREATE INDEX idx_report_admin ON Reports(admin_id);  -- Index on admin_id in Reports table

-- Create indexes to optimize query performance (optional)
CREATE INDEX idx_room_trusted_user ON RoomTrustedUsers(user_id);  -- Index on user_id in RoomTrustedUsers table
CREATE INDEX idx_blacklist_user ON Blacklist(user_id);            -- Index on user_id in Blacklist table
