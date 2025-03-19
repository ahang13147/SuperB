USE `booking_system_db`;


-- 触发器：当 Bookings 表中插入新记录时，更新对应 Room_availability 的 availability 为 2（已预订）。
DELIMITER //
CREATE TRIGGER update_availability_on_booking_insert
AFTER INSERT ON Bookings
FOR EACH ROW
BEGIN
    IF NEW.status = 'approved' THEN
        UPDATE Room_availability
        SET availability = 2
        WHERE room_id = NEW.room_id
          AND available_date = NEW.booking_date
          AND available_begin = NEW.start_time
          AND available_end = NEW.end_time;
    END IF;
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





DELIMITER //

CREATE PROCEDURE reassignBookings(IN unavailable_room_id INT)
BEGIN
    DECLARE v_booking_id INT;
    DECLARE v_user_id INT;
    DECLARE v_start_time TIME;
    DECLARE v_end_time TIME;
    DECLARE v_booking_date DATE;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR
         SELECT booking_id, user_id, start_time, end_time, booking_date
         FROM Bookings
         WHERE room_id = unavailable_room_id
           AND booking_date >= CURDATE()
           AND status NOT IN ('canceled', 'rejected', 'failed');

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;
    read_loop: LOOP
       FETCH cur INTO v_booking_id, v_user_id, v_start_time, v_end_time, v_booking_date;
       IF done THEN
           LEAVE read_loop;
       END IF;

       -- Set capacity threshold (for example, 10 seats)
       SET @capacity_threshold = 10;

       -- Get the original room's capacity and equipment details
       SELECT capacity, equipment INTO @orig_capacity, @orig_equipment
       FROM Rooms
       WHERE room_id = unavailable_room_id;

       -- Find a suitable replacement room:
       -- 1. The room must be available (room_status = 0)
       -- 2. Capacity difference within the threshold
       -- 3. Equipment matches (exact match in this example)
       -- 4. No booking conflicts for the same date and time slot
       SELECT room_id INTO @new_room_id FROM Rooms
       WHERE room_status = 0
         AND room_id <> unavailable_room_id
         AND ABS(capacity - @orig_capacity) <= @capacity_threshold
         AND equipment = @orig_equipment
         AND room_id NOT IN (
             SELECT room_id FROM Bookings
             WHERE booking_date = v_booking_date
               AND ((start_time < v_end_time) AND (end_time > v_start_time))
         )
       ORDER BY ABS(capacity - @orig_capacity) ASC
       LIMIT 1;

       IF @new_room_id IS NOT NULL THEN
          -- Update booking record with the new room and mark as 'changed'
          UPDATE Bookings
          SET room_id = @new_room_id,
              status = 'changed',
              reason = CONCAT('Room reassigned to room ID: ', @new_room_id)
          WHERE booking_id = v_booking_id;

          INSERT INTO Notifications(user_id, message, notification_action)
          VALUES (v_user_id, CONCAT('Your booking has been reassigned to room ', @new_room_id, '.'), 'reminder');
       ELSE
          -- If no suitable replacement room is found, mark the booking as 'failed'
          UPDATE Bookings
          SET status = 'failed',
              reason = 'No suitable replacement room found'
          WHERE booking_id = v_booking_id;

          INSERT INTO Notifications(user_id, message, notification_action)
          VALUES (v_user_id, 'No suitable replacement room found. Your booking has been cancelled.', 'cancellation');
       END IF;

    END LOOP;
    CLOSE cur;
END //
DELIMITER ;




DROP TRIGGER IF EXISTS trg_after_room_unavailable;

DELIMITER //

CREATE TRIGGER trg_after_room_unavailable
AFTER UPDATE ON Rooms
FOR EACH ROW
BEGIN
    IF (NEW.room_status = 3 AND OLD.room_status <> 3)
    OR (NEW.room_status = 2 AND OLD.room_status <> 2) THEN
         CALL reassignBookings(NEW.room_id);
    END IF;
END //

DELIMITER ;



DELIMITER //

-- 触发器：在插入一条 Issue 后自动发送通知，并根据 Issue 状态更新 Rooms 表的 room_status
CREATE TRIGGER after_issue_insert
AFTER INSERT ON Issues
FOR EACH ROW
BEGIN
    -- 插入通知（保持原来的内容）
    INSERT INTO Notifications (user_id, message, notification_action)
    VALUES (
        NULL,
        CONCAT('New issue created for room ', NEW.room_id, ': ', NEW.issue, '. Status: ', NEW.status),
        'alert'
    );

    -- 根据 Issue 的状态更新 Rooms 表的 room_status
    IF NEW.status = 'resolved' THEN
        UPDATE Rooms SET room_status = 0 WHERE room_id = NEW.room_id;
    ELSEIF NEW.status IN ('fault', 'in_maintenance') THEN
        UPDATE Rooms SET room_status = 1 WHERE room_id = NEW.room_id;
    ELSEIF NEW.status = 'severe' THEN
        UPDATE Rooms SET room_status = 2 WHERE room_id = NEW.room_id;
    END IF;
END;
//

-- 触发器：在更新 Issue 时，如果 status 发生变化，则自动发送通知，并根据新状态更新 Rooms 表的 room_status
CREATE TRIGGER after_issue_update
AFTER UPDATE ON Issues
FOR EACH ROW
BEGIN
    IF NEW.status <> OLD.status THEN
        INSERT INTO Notifications (user_id, message, notification_action)
        VALUES (
            NULL,
            CONCAT('Issue ', NEW.issue_id, ' status changed from ', OLD.status, ' to ', NEW.status),
            'changed'
        );

        -- 根据新的 Issue 状态更新 Rooms 表的 room_status
        IF NEW.status = 'resolved' THEN
            UPDATE Rooms SET room_status = 0 WHERE room_id = NEW.room_id;
        ELSEIF NEW.status IN ('fault', 'in_maintenance') THEN
            UPDATE Rooms SET room_status = 1 WHERE room_id = NEW.room_id;
        ELSEIF NEW.status = 'severe' THEN
            UPDATE Rooms SET room_status = 2 WHERE room_id = NEW.room_id;
        END IF;
    END IF;
END;
//

DELIMITER ;
