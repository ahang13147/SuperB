
-- @version: 3/11/2025
-- @author: Xin Yu, Zibang Nie, Siyan Guo
-- @description: This SQL script creates a advanced sql to manage Room_availability updates when a Booking is inserted or deleted.
-- ADD:add two  advanced sql(cancel, and failed)

USE `booking_system_db`;


-- 触发器：当从 Bookings 表删除记录时，更新 Room_availability 表中的 availability 为 0
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


-- 触发器：当 Bookings 表中的记录的 status 字段被更新为 'approved' 时，更新 Room_availability 中的 availability 为 2
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


DELIMITER ;


DELIMITER //
-- 触发器：当 Bookings 表中插入新记录时，更新 Room_availability 中的 availability 为 2
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


DELIMITER //

-- 当Bookings表中status字段为pending时，如果这一条booking对应的Room_availability表中的availability字段变为2，则这一条booking对应的status变为failed。
CREATE TRIGGER update_status_on_room_availability_change
AFTER UPDATE ON Room_availability
FOR EACH ROW
BEGIN
    -- Check if the availability has changed to 2 (booked)
    IF NEW.availability = 2 THEN
        -- Update the corresponding booking's status to 'failed' if it's still 'pending'
        UPDATE Bookings
        SET status = 'failed'
        WHERE room_id = NEW.room_id
          AND booking_date = NEW.available_date
          AND start_time = NEW.available_begin
          AND end_time = NEW.available_end
          AND status = 'pending';
    END IF;
END //

DELIMITER ;



DELIMITER //
-- 这是我现在的数据库。我希望当Bookings中的  status字段变成'canceled',时，Room_availability中的availability变为0
CREATE TRIGGER update_availability_on_booking_canceled
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    -- Check if the status has changed to 'canceled'
    IF NEW.status = 'canceled' AND OLD.status != 'canceled' THEN
        -- Update the corresponding Room_availability's availability to 0
        UPDATE Room_availability
        SET availability = 0
        WHERE room_id = NEW.room_id
          AND available_date = NEW.booking_date
          AND available_begin = NEW.start_time
          AND available_end = NEW.end_time;
    END IF;
END //

DELIMITER ;

