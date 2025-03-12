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


-- -- Trigger: 当 Bookings 表中记录的 status 字段更新为 'approved' 时，
-- -- 将对应 Room_availability 的 availability 更新为 2（已预订）。
-- DELIMITER //
-- CREATE TRIGGER update_availability_on_booking_approve
-- AFTER UPDATE ON Bookings
-- FOR EACH ROW
-- BEGIN
--     IF NEW.status = 'approved' AND OLD.status != 'approved' THEN
--         UPDATE Room_availability
--         SET availability = 2
--         WHERE room_id = NEW.room_id
--           AND available_date = NEW.booking_date
--           AND available_begin = NEW.start_time
--           AND available_end = NEW.end_time;
--     END IF;
-- END //
-- DELIMITER ;

-- -- Trigger: 当 Bookings 表中插入新记录时，将对应 Room_availability 的 availability 更新为 2（已预订）。
-- DELIMITER //
-- CREATE TRIGGER update_availability_on_booking_insert
-- AFTER INSERT ON Bookings
-- FOR EACH ROW
-- BEGIN
--     UPDATE Room_availability
--     SET availability = 2
--     WHERE room_id = NEW.room_id
--       AND available_date = NEW.booking_date
--       AND available_begin = NEW.start_time
--       AND available_end = NEW.end_time;
-- END //
-- DELIMITER ;

-- -- Trigger: 当 Bookings 表中记录的 status 字段更新为 'canceled' 时，
-- -- 将对应 Room_availability 的 availability 更新为 0（可用）。
-- DELIMITER //
-- CREATE TRIGGER update_availability_on_booking_canceled
-- AFTER UPDATE ON Bookings
-- FOR EACH ROW
-- BEGIN
--     IF NEW.status = 'canceled' AND OLD.status != 'canceled' THEN
--         UPDATE Room_availability
--         SET availability = 0
--         WHERE room_id = NEW.room_id
--           AND available_date = NEW.booking_date
--           AND available_begin = NEW.start_time
--           AND available_end = NEW.end_time;
--     END IF;
-- END //
-- DELIMITER ;

-- -- 创建中间表，用于存储需要更新状态的 Bookings 的信息
-- CREATE TABLE IF NOT EXISTS BookingStatusUpdateQueue (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     room_id INT NOT NULL,
--     booking_date DATE NOT NULL,
--     start_time TIME NOT NULL,
--     end_time TIME NOT NULL,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- Trigger: 当 Room_availability 表中 availability 更新为 2（已预订）时，
-- -- 将对应的房间和时间段信息插入队列表，以便后续更新 Bookings 表中 pending 状态的记录为 'failed'
-- DELIMITER //
-- CREATE TRIGGER queue_booking_status_update_on_room_availability_change
-- AFTER UPDATE ON Room_availability
-- FOR EACH ROW
-- BEGIN
--     IF NEW.availability = 2 THEN
--         INSERT INTO BookingStatusUpdateQueue (room_id, booking_date, start_time, end_time)
--         VALUES (NEW.room_id, NEW.available_date, NEW.available_begin, NEW.available_end);
--     END IF;
-- END //
-- DELIMITER ;

-- -- 创建存储过程，用于处理队列表中待更新的预订记录
-- DELIMITER //
-- CREATE PROCEDURE ProcessBookingStatusUpdateQueue()
-- BEGIN
--     DECLARE done INT DEFAULT 0;
--     DECLARE b_room_id INT;
--     DECLARE b_booking_date DATE;
--     DECLARE b_start_time TIME;
--     DECLARE b_end_time TIME;
--     DECLARE cur CURSOR FOR
--         SELECT room_id, booking_date, start_time, end_time FROM BookingStatusUpdateQueue;
--     DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;
--
--     OPEN cur;
--     read_loop: LOOP
--         FETCH cur INTO b_room_id, b_booking_date, b_start_time, b_end_time;
--         IF done THEN
--             LEAVE read_loop;
--         END IF;
--         UPDATE Bookings
--         SET status = 'failed'
--         WHERE room_id = b_room_id
--           AND booking_date = b_booking_date
--           AND start_time = b_start_time
--           AND end_time = b_end_time
--           AND status = 'pending';
--     END LOOP;
--     CLOSE cur;
--     -- 清空队列表
--     DELETE FROM BookingStatusUpdateQueue;
-- END //
-- DELIMITER ;

-- -- 创建定时事件，每隔 1 分钟调用一次存储过程处理队列表
-- DELIMITER //
-- CREATE EVENT IF NOT EXISTS ProcessBookingStatusUpdateQueueEvent
-- ON SCHEDULE EVERY 1 MINUTE
-- DO
--     CALL ProcessBookingStatusUpdateQueue() //
-- DELIMITER ;
