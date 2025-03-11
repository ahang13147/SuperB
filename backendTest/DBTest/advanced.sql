
-- @version: 3/11/2025
-- @author: Xin Yu, Zibang Nie, Siyan Guo
-- @description: This SQL script creates a advanced sql to manage Room_availability updates when a Booking is inserted or deleted.


USE `booking_system_db`;



DELIMITER //

CREATE TRIGGER update_availability_on_booking_delete
AFTER DELETE ON Bookings
FOR EACH ROW
BEGIN
    -- 更新对应的 Room_availability 的 availability 为 0
    UPDATE Room_availability
    SET availability = 0
    WHERE room_id = OLD.room_id
      AND available_date = OLD.booking_date
      AND available_begin = OLD.start_time
      AND available_end = OLD.end_time;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER update_availability_on_booking_approve
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    -- Check if the status has changed to 'approved'
    IF NEW.status = 'approved' AND OLD.status != 'approved' THEN
        -- Update corresponding Room_availability's availability to 2 (booked)
        UPDATE Room_availability
        SET availability = 2
        WHERE room_id = NEW.room_id
          AND available_date = NEW.booking_date
          AND available_begin = NEW.start_time
          AND available_end = NEW.end_time;
    END IF;
END //

DELIMITER ;

-- DELIMITER //

-- -- Trigger to update status to 'canceled' when a booking is deleted
-- CREATE TRIGGER update_status_on_booking_delete
-- BEFORE DELETE ON Bookings
-- FOR EACH ROW
-- BEGIN
--     -- Update the status of the booking to 'canceled'
--     UPDATE Bookings
--     SET status = 'canceled'
--     WHERE booking_id = OLD.booking_id;
-- END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER update_availability_on_booking_insert
AFTER INSERT ON Bookings
FOR EACH ROW
BEGIN
    -- 更新对应的 Room_availability 的 availability 为 2
    UPDATE Room_availability
    SET availability = 2
    WHERE room_id = NEW.room_id
      AND available_date = NEW.booking_date
      AND available_begin = NEW.start_time
      AND available_end = NEW.end_time;
END //

DELIMITER ;
