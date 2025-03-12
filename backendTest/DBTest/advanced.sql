USE `booking_system_db`;

-- 触发器：当 Bookings 表中插入新记录时，更新对应 Room_availability 的 availability 为 2（已预订）。
DELIMITER //
CREATE TRIGGER update_availability_on_booking_insert
AFTER INSERT ON Bookings
FOR EACH ROW
BEGIN
    UPDATE Room_availability
    SET availability = 2
    WHERE room_id = NEW.room_id
      AND available_date = NEW.booking_date
      AND available_begin = NEW.start_time
      AND available_end = NEW.end_time;
END //
DELIMITER ;

-- 触发器：当 Bookings 表中记录的 status 字段更新为 'approved' 时，
-- 更新对应 Room_availability 的 availability 为 2（已预订）。
DELIMITER //
CREATE TRIGGER update_availability_on_booking_approve
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    IF NEW.status = 'approved' AND OLD.status <> 'approved' THEN
        UPDATE Room_availability
        SET availability = 2
        WHERE room_id = NEW.room_id
          AND available_date = NEW.booking_date
          AND available_begin = NEW.start_time
          AND available_end = NEW.end_time;
    END IF;
END //
DELIMITER ;

-- 触发器：当 Bookings 表中记录的 status 字段更新为 'canceled' 时，
-- 更新对应 Room_availability 的 availability 为 0（可用）。
DELIMITER //
CREATE TRIGGER update_availability_on_booking_canceled
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    IF NEW.status = 'canceled' AND OLD.status <> 'canceled' THEN
        UPDATE Room_availability
        SET availability = 0
        WHERE room_id = NEW.room_id
          AND available_date = NEW.booking_date
          AND available_begin = NEW.start_time
          AND available_end = NEW.end_time;
    END IF;
END //
DELIMITER ;

