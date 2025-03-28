-- @version: 3/17/2025
-- @author: Xin Yu, Siyan Guo, Zibang Nie
-- @description: This SQL script creates a booking system database, which includes tables for Users, Rooms, Bookings, Approvals, Notifications, and Reports.
-- It provides a structure to manage users, room bookings, approval processes, notifications, and report generation.
-- ADD: new field of room

USE `booking_system_db`;


<<<<<<< HEAD
INSERT INTO Users (username, email, phone_number, role) VALUES
('Alex', 'BookingSystem.SuperB@outlook.com', '18889635156', 'student'),
('Xin Yu', '2543651@dundee.ac.uk', '18889935156', 'admin'),
('Siyan Guo', '2543137@dundee.ac.uk', 'hash3', 'admin'),
('Yi Su', '2544215@dundee.ac.uk', 'hash4', 'professor'),
('Marco_Admin', 'diicsupriority@outlook.com', '17779635156', 'admin'),
('Xv Liu', '2543149@dundee.ac.uk', '18879635156', 'tutor'),
('Zibang Nie', '2542881@dundee.ac.uk', '19979635156', 'student'),
('Guanhang Zhang ', '2542841@dundee.ac.uk', '19979635156', 'student'),
('Jiawei You', '2542692@dundee.ac.uk', '19979635333', 'student'),
('Yi Dai', '2542942@dundee.ac.uk', '19979635999', 'student'),
('tutor3', 'tutor2@example.com', 'hash8', 'tutor'),
('student4', 'student3@example.com', 'hash9', 'student'),
('tutor4', 'tutor3333@example.com', 'hash8', 'tutor'),
('student5', 'student5@example.com', 'hash9', 'student'),
('prof3', 'prof3@example.com', 'hash10', 'professor');
=======
INSERT INTO Users (username, email, phone_number, role, avatar_path) VALUES
('Alex', 'BookingSystem.SuperB@outlook.com', '18889635156', 'student',''),
('Xin Yu', '2543651@dundee.ac.uk', '18889935156', 'admin',''),
('Siyan Guo', '2543137@dundee.ac.uk', 'hash3', 'admin',''),
('Yi Su', '2544215@dundee.ac.uk', 'hash4', 'student',''),
('Marco_Admin', 'diicsupriority@outlook.com', '17779635156', 'admin',''),
('Xv Liu', '2543149@dundee.ac.uk', '18879635156', 'tutor',''),
('Zibang Nie', '2542881@dundee.ac.uk', '19979635156', 'student',''),
('Guanhang Zhang ', '2542841@dundee.ac.uk', '19979635156', 'student',''),
('Jiawei You', '2542692@dundee.ac.uk', '19979635333', 'student',''),
('Yi Dai', '2542942@dundee.ac.uk', '19979635999', 'student',''),
('tutor3', 'tutor2@example.com', 'hash8', 'tutor',''),
('student4', 'student3@example.com', 'hash9', 'student',''),
('tutor4', 'tutor3333@example.com', 'hash8', 'tutor',''),
('student5', 'student5@example.com', 'hash9', 'student',''),
('prof3', 'prof3@example.com', 'hash10', 'professor','');
>>>>>>> feature/email

INSERT INTO Rooms (room_name, capacity, equipment, location, room_type,room_status)
VALUES
('101', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('102', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('103', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('104', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('105', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('106', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('107', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('108', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('109', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('110', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('111', 30, 'Projector, Whiteboard', 'DIICSU Ground Floor',0,0),
('635', 60, 'Projector, Whiteboard', 'DIICSU SIX Floor',1,0),
('622', 42, 'Projector, Whiteboard', 'DIICSU SIX Floor',1,0),
('formal meeting room', 14, 'Projector,Board Room Configuration', 'DIICSU Ground Floor',1,0),
('informal meeting room', 12, 'Projector,Open Configuration', 'DIICSU Ground Floor',1,0),
('634', 10, 'Projector,Board Room Configuration', 'DIICSU 634',2,0);

-- SET @current_date = CURRENT_DATE();
--
--
-- -- 更新Room_availability的日期为动态范围
-- INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability) VALUES
-- -- 过去3天到未来7天的数据
-- (1, '09:00:00', '12:00:00', DATE_SUB(@current_date, INTERVAL 3 DAY), 0),
-- (1, '13:00:00', '17:00:00', DATE_SUB(@current_date, INTERVAL 2 DAY), 1),
-- (2, '10:00:00', '14:00:00', DATE_SUB(@current_date, INTERVAL 1 DAY), 0),
-- (2, '15:00:00', '18:00:00', @current_date, 2),
-- (3, '08:00:00', '10:00:00', DATE_ADD(@current_date, INTERVAL 1 DAY), 0),
-- (3, '11:00:00', '13:00:00', DATE_ADD(@current_date, INTERVAL 2 DAY), 1),
-- (4, '09:00:00', '12:00:00', DATE_ADD(@current_date, INTERVAL 3 DAY), 0),
-- (12, '10:00:00', '12:00:00', DATE_ADD(@current_date, INTERVAL 4 DAY), 0),
-- (5, '13:00:00', '15:00:00', DATE_ADD(@current_date, INTERVAL 5 DAY), 1);


INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status, reason)
VALUES
<<<<<<< HEAD
(1, 1, '08:00:00', '08:45:00', '2025-03-17', 'approved', ''),
(5, 1, '08:55:00', '09:40:00', '2025-03-18', 'approved', ''),
(1, 2, '10:00:00', '10:45:00', '2025-03-19', 'pending', 'Awaiting approval'),
(5, 2, '10:55:00', '11:40:00', '2025-03-17', 'approved', ''),
(1, 3, '14:00:00', '14:45:00', '2025-03-18', 'approved', ''),
(5, 3, '14:55:00', '15:40:00', '2025-03-19', 'approved', ''),
(1, 4, '16:00:00', '16:45:00', '2025-03-17', 'pending', 'Awaiting approval'),
(5, 4, '16:55:00', '17:40:00', '2025-03-18', 'approved', ''),
(1, 5, '19:00:00', '19:45:00', '2025-03-19', 'approved', ''),
(5, 5, '19:55:00', '20:40:00', '2025-03-17', 'approved', ''),
(7, 6, '08:00:00', '08:45:00', '2025-03-19', 'approved', '');
=======
(1, 1, '08:00:00', '08:45:00', '2025-03-17', 'finished', ''),
(5, 1, '08:55:00', '09:40:00', '2025-03-18', 'finished', ''),
(1, 2, '10:00:00', '10:45:00', '2025-03-19', 'finished', 'Awaiting approval'),
(5, 2, '10:55:00', '11:40:00', '2025-03-17', 'finished', ''),
(1, 3, '14:00:00', '14:45:00', '2025-03-18', 'finished', ''),
(5, 3, '14:55:00', '15:40:00', '2025-03-19', 'finished', ''),
(1, 4, '16:00:00', '16:45:00', '2025-03-17', 'finished', 'Awaiting approval'),
(5, 4, '16:55:00', '17:40:00', '2025-03-18', 'finished', ''),
(1, 5, '19:00:00', '19:45:00', '2025-03-19', 'finished', ''),
(5, 1, '10:00:00', '10:40:00', '2025-03-27', 'finished', '');

>>>>>>> feature/email

-- Insert sample data into Notifications table
INSERT INTO Notifications (user_id, message, notification_action,status) VALUES
(3, 'Your booking for Room A has been approved.', 'confirmation','unread'),
(2, 'Your booking for Room B has been approved.', 'confirmation','unread'),
(4, 'Your booking for Room C is pending reassignment.', 'reminder','unread'),
(3, 'Your booking for Room D has been approved.', 'confirmation','unread');

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
(12, 2, '2025-03-01', '10:00:00', '2025-03-01', '10:00:00', '2025-03-31', '23:59:59', 'Repeated no-shows'),
(12, 5, '2025-03-02', '11:00:00', '2025-03-02', '11:00:00', '2025-04-02', '23:59:59', 'Misuse of room equipment'),
(13, 3, '2025-03-03', '12:00:00', '2025-03-03', '12:00:00', '2025-03-10', '23:59:59', 'Violation of rules'),
(14, 5, '2025-03-04', '13:00:00', '2025-03-04', '13:00:00', '2025-03-11', '23:59:59', 'Unauthorized access');

INSERT INTO Issues (room_id, issue, status, start_date, start_time, end_date, end_time, added_by) VALUES
(1, 'Projector not working', 'fault', '2025-03-17', '08:30:00', NULL, NULL, 1),
(2, 'Air conditioning malfunction', 'in_maintenance', '2025-03-18', '10:00:00', '2025-03-18', '15:00:00', 2),
(3, 'Broken chair in conference room', 'resolved', '2025-03-19', '09:00:00', '2025-03-19', '11:00:00', 1),
(4, 'Severe water leakage detected', 'severe', '2025-03-17', '14:00:00', NULL, NULL, 3),
(2, 'Light bulb flickering', 'fault', '2025-03-20', '13:00:00', NULL, NULL, 2),
(1, 'Door malfunction - not closing properly', 'in_maintenance', '2025-03-20', '08:00:00', NULL, NULL, 1);


