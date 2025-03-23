-- delete_records_with_all_conditions.sql
-- This SQL script contains delete queries for each table in the booking system,
-- where parameters can be combined to delete records based on any combination of fields.

-- 1.1 Delete User by any combination of user_id, username, email, role, or any other combination of parameters
DELETE FROM Users
WHERE
  (user_id = ? OR ? IS NULL) AND
  (username = ? OR ? IS NULL) AND
  (email = ? OR ? IS NULL) AND
  (role = ? OR ? IS NULL);

-- 1.2 Delete Room by any combination of room_id, room_name, capacity, location, or any other combination of parameters
DELETE FROM Rooms
WHERE
  (room_id = ? OR ? IS NULL) AND
  (room_name = ? OR ? IS NULL) AND
  (capacity = ? OR ? IS NULL) AND
  (location = ? OR ? IS NULL);

-- 1.3 Delete Room Availability by any combination of room_id, available_date, available_begin, available_end, or any other combination of parameters
DELETE FROM Room_availability
WHERE
  (room_id = ? OR ? IS NULL) AND
  (available_date = ? OR ? IS NULL) AND
  (available_begin = ? OR ? IS NULL) AND
  (available_end = ? OR ? IS NULL);

-- 1.4 Delete Booking by room_name, start_time, end_time, booking_date, or any other combination of parameters
DELETE FROM Bookings
WHERE
  room_id = (SELECT room_id FROM Rooms WHERE room_name = ?) AND
  start_time = ? AND
  end_time = ? AND
  booking_date = ? AND
  (status = ? OR ? IS NULL);

-- 1.5 Delete Approval by any combination of approval_id, booking_id, admin_id, approval_status, or any other combination of parameters
DELETE FROM Approvals
WHERE
  (approval_id = ? OR ? IS NULL) AND
  (booking_id = ? OR ? IS NULL) AND
  (admin_id = ? OR ? IS NULL) AND
  (approval_status = ? OR ? IS NULL);

-- 1.6 Delete Notification by any combination of notification_id, user_id, notification_type, status, or any other combination of parameters
DELETE FROM Notifications
WHERE
  (notification_id = ? OR ? IS NULL) AND
  (user_id = ? OR ? IS NULL) AND
  (notification_type = ? OR ? IS NULL) AND
  (status = ? OR ? IS NULL);

-- 1.7 Delete Report by any combination of report_id, admin_id, report_type, or any other combination of parameters
DELETE FROM Reports
WHERE
  (report_id = ? OR ? IS NULL) AND
  (admin_id = ? OR ? IS NULL) AND
  (report_type = ? OR ? IS NULL);

-- Additional logic to handle foreign key constraints:
-- Ensure we do not violate foreign key constraints by deleting in a dependent order.

-- Deleting related notifications for a specific user before deleting the user.
DELETE FROM Notifications WHERE user_id = ?;

-- Deleting related approvals for a specific booking before deleting the booking.
DELETE FROM Approvals WHERE booking_id = ?;

-- Deleting related room availability before deleting the room.
DELETE FROM Room_availability WHERE room_id = ?;
