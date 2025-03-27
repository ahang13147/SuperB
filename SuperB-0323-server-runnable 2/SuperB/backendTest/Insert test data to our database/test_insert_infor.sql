USE `booking_system_db`;

INSERT INTO Users (username, email, password_hash, role)
VALUES
('admin_user', 'admin@example.com', 'hashed_password1', 'admin'),
('professor_user', 'professor@example.com', 'hashed_password2', 'professor'),
('student_user', 'student@example.com', 'hashed_password3', 'student'),
('tutor_user', 'tutor@example.com', 'hashed_password4', 'tutor');


INSERT INTO Rooms (room_name, capacity, equipment, location)
VALUES
('635', 20, 'Projector, Whiteboard', 'Building 1, Floor 2'),
('119', 30, 'Projector, Computer', 'Building 1, Floor 3'),
('117', 10, 'Whiteboard', 'Building 2, Floor 1');


INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability)
VALUES
(1, '08:00', '10:00', '2025-03-06', 0),
(2, '10:00', '12:00', '2025-03-06', 0),
(3, '13:00', '15:00', '2025-03-06', 1);



INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status)
VALUES
(1, 1, '08:00', '10:00', '2025-03-06', 'pending'),
(2, 2, '10:00', '12:00', '2025-03-06', 'approved'),
(3, 3, '13:00', '15:00', '2025-03-06', 'canceled');


INSERT INTO Approvals (booking_id, admin_id, approval_status, approved_at)
VALUES
(1, 1, 'approved', '2025-03-05 10:00:00'),
(2, 1, 'approved', '2025-03-05 11:00:00'),
(3, 1, 'rejected', '2025-03-05 12:00:00');


INSERT INTO Notifications (user_id, message, notification_type, status)
VALUES
(1, 'Your booking for Room A has been approved.', 'confirmation', 'unread'),
(2, 'Reminder: Your booking for Room B is starting soon.', 'reminder', 'unread'),
(3, 'Your booking for Room C has been canceled.', 'cancellation', 'read');


INSERT INTO Reports (admin_id, report_type, generated_at, data)
VALUES
(1, 'PDF', '2025-03-05 14:00:00', '{"total_bookings": 10, "approved_bookings": 8, "canceled_bookings": 2}');

