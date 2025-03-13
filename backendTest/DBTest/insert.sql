-- @version: 3/11/2025
-- @author: Xin Yu, Siyan Guo, Zibang Nie
-- @description: This SQL script creates a booking system database, which includes tables for Users, Rooms, Bookings, Approvals, Notifications, and Reports.
-- It provides a structure to manage users, room bookings, approval processes, notifications, and report generation.
-- ADD: new field of room

USE `booking_system_db`;

INSERT INTO Users (username, email, phone_number, role) VALUES
('admin1', 'admin1@example.com', 'hash1', 'admin'),
('prof1', 'prof1@example.com', 'hash2', 'professor'),
('student1', 'student1@example.com', 'hash3', 'student'),
('tutor1', 'tutor1@example.com', 'hash4', 'tutor'),
('admin2', 'admin2@example.com', 'hash5', 'admin'),
('prof2', 'prof2@example.com', 'hash6', 'professor'),
('student2', 'student2@example.com', 'hash7', 'student'),
('tutor2', 'tutor2@example.com', 'hash8', 'tutor'),
('student3', 'student3@example.com', 'hash9', 'student'),
('prof3', 'prof3@example.com', 'hash10', 'professor');

INSERT INTO Rooms (room_name, capacity, equipment, location, room_type)
VALUES
('101', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('102', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('103', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('104', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('105', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('106', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('107', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('108', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('109', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('110', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('111', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0),
('635', 60, 'Projector, Whiteboard', 'DIICSU SIX Floor',1),
('622', 42, 'Projector, Whiteboard', 'DIICSU SIX Floor',1),
('formal meeting room', 14, 'Projector,Board Room Configuration', 'DIICSU Ground Floor',1),
('informal meeting room', 12, 'Projector,Open Configuration', 'DIICSU Ground Floor',1),
('634', 10, 'Projector,Board Room Configuration', 'DIICSU 634',2);

INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability) VALUES
(1, '09:00:00', '12:00:00', '2025-03-05', 0),
(1, '13:00:00', '17:00:00', '2025-03-05', 1),
(2, '10:00:00', '14:00:00', '2025-03-05', 0),
(2, '15:00:00', '18:00:00', '2025-03-05', 2),
(3, '08:00:00', '10:00:00', '2025-03-06', 0),
(3, '11:00:00', '13:00:00', '2025-03-06', 1),
(4, '09:00:00', '12:00:00', '2025-03-06', 0),
(4, '14:00:00', '16:00:00', '2025-03-06', 2),
(12, '10:00:00', '12:00:00', '2025-03-07', 0),
(5, '13:00:00', '15:00:00', '2025-03-07', 1);


INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status, reason)
VALUES
(2, 1, '10:00:00', '11:00:00', '2025-03-05', 'approved', 'Regular class'),
(3, 2, '14:00:00', '15:00:00', '2025-03-05', 'pending', 'Study group'),
(4, 3, '16:00:00', '17:00:00', '2025-03-05', 'rejected', 'Insufficient equipment');


INSERT INTO Notifications (user_id, message, notification_type, status)
VALUES
(1, 'Your booking for Room A has been approved.', 'confirmation', 'unread'),
(2, 'Reminder: Your booking for Room B is starting soon.', 'reminder', 'unread'),
(3, 'Your booking for Room C has been canceled.', 'cancellation', 'read'),
(1, 'Reminder: Your booking for Room A is starting soon.', 'reminder', 'unread'),
(2, 'Your booking for Room B has been approved.', 'confirmation', 'read'),
(3, 'Your booking for Room C has been rejected.', 'cancellation', 'unread');

INSERT INTO Reports (admin_id, report_type, generated_at, data)
VALUES
(1, 'PDF', '2025-03-05 14:00:00', '{"total_bookings": 10, "approved_bookings": 8, "canceled_bookings": 2}'),
(1, 'Excel', '2025-03-06 09:00:00', '{"total_bookings": 15, "approved_bookings": 12, "canceled_bookings": 3}');

INSERT INTO RoomTrustedUsers (room_id, user_id, added_by, added_date, added_time, notes) VALUES
(12, 3, 1, '2025-03-01', '10:00:00', 'Trusted for academic purposes'),
(12, 4, 1, '2025-03-01', '11:00:00', 'Trusted for tutoring sessions'),
(13, 5, 5, '2025-03-02', '09:00:00', 'Trusted for workshops'),
(14, 6, 5, '2025-03-02', '10:00:00', 'Trusted for group meetings'),
(15, 7, 1, '2025-03-03', '14:00:00', 'Trusted for study groups'),
(12, 8, 5, '2025-03-03', '15:00:00', 'Trusted for project work'),
(12, 9, 1, '2025-03-04', '12:00:00', 'Trusted for presentations'),
(13, 10, 5, '2025-03-04', '13:00:00', 'Trusted for discussions'),
(14, 3, 1, '2025-03-05', '16:00:00', 'Trusted for academic purposes'),
(15, 4, 5, '2025-03-05', '17:00:00', 'Trusted for tutoring sessions');


INSERT INTO Blacklist (user_id, added_by, added_date, added_time, start_date, start_time, end_date, end_time, reason) VALUES
(3, 1, '2025-03-01', '10:00:00', '2025-03-01', '10:00:00', '2025-03-31', '23:59:59', 'Repeated no-shows'),
(4, 5, '2025-03-02', '11:00:00', '2025-03-02', '11:00:00', '2025-04-02', '23:59:59', 'Misuse of room equipment'),
(5, 1, '2025-03-03', '12:00:00', '2025-03-03', '12:00:00', '2025-03-10', '23:59:59', 'Violation of rules'),
(6, 5, '2025-03-04', '13:00:00', '2025-03-04', '13:00:00', '2025-03-11', '23:59:59', 'Unauthorized access'),
(7, 1, '2025-03-05', '14:00:00', '2025-03-05', '14:00:00', '2025-03-12', '23:59:59', 'Disruptive behavior'),
(8, 5, '2025-03-06', '15:00:00', '2025-03-06', '15:00:00', '2025-03-13', '23:59:59', 'Repeated complaints'),
(9, 1, '2025-03-07', '16:00:00', '2025-03-07', '16:00:00', '2025-03-14', '23:59:59', 'Policy violation'),
(10, 5, '2025-03-08', '17:00:00', '2025-03-08', '17:00:00', '2025-03-15', '23:59:59', 'Unauthorized bookings'),
(3, 1, '2025-03-09', '18:00:00', '2025-03-09', '18:00:00', '2025-03-16', '23:59:59', 'Repeated no-shows'),
(4, 5, '2025-03-10', '19:00:00', '2025-03-10', '19:00:00', '2025-03-17', '23:59:59', 'Misuse of room equipment');