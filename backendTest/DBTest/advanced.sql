-- @version: 3/18/2025
-- @author: Xin Yu, Siyan Guo, Zibang Nie
-- @description: This SQL script creates a booking system database, which includes tables for Users, Rooms, Bookings, Approvals, Notifications, and Reports.
-- It provides a structure to manage users, room bookings, approval processes, notifications, and report generation.
-- ADD: add new feild of rooms


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


-- 触发器：当 Bookings 表中记录的 status 字段更新为 'approved'或者changed时候 时，
-- 更新对应 Room_availability 的 availability 为 2（已预订）。
DELIMITER //
CREATE TRIGGER update_availability_on_booking_approve_or_changed
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    IF NEW.status IN ('approved', 'changed') THEN
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
    DECLARE v_username VARCHAR(255);
    DECLARE v_orig_roomname VARCHAR(255);
    DECLARE v_new_roomname VARCHAR(255);
    DECLARE done INT DEFAULT FALSE;

    -- Cursor: 获取所有预定了该不可用房间的预订记录（且日期大于等于今天，且状态未取消、拒绝或失败）
    DECLARE cur CURSOR FOR
         SELECT booking_id, user_id, start_time, end_time, booking_date
         FROM Bookings
         WHERE room_id = unavailable_room_id
           AND booking_date >= CURDATE()
           AND status NOT IN ('canceled', 'rejected', 'failed');

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- 获取原房间名称
    SELECT room_name INTO v_orig_roomname FROM Rooms WHERE room_id = unavailable_room_id;

    OPEN cur;
    read_loop: LOOP
       FETCH cur INTO v_booking_id, v_user_id, v_start_time, v_end_time, v_booking_date;
       IF done THEN
           LEAVE read_loop;
       END IF;

       -- 获取预定该房间的用户的用户名
       SELECT username INTO v_username FROM Users WHERE user_id = v_user_id;

       -- 设置容量允许的误差阈值（例如10个座位）
       SET @capacity_threshold = 10;

       -- 获取原房间的容量和设备信息
       SELECT capacity, equipment INTO @orig_capacity, @orig_equipment
       FROM Rooms
       WHERE room_id = unavailable_room_id;

       -- 查找一个合适的替代房间：
       -- 1. 该房间必须可用（room_status = 0）
       -- 2. 容量差在允许阈值内
       -- 3. 设备要求（这里要求完全匹配）
       -- 4. 在预定的日期和时间段内，该房间没有冲突预定
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
          -- 如果找到合适的替代房间，获取新房间名称
          SELECT room_name INTO v_new_roomname FROM Rooms WHERE room_id = @new_room_id;

          -- 更新预定记录，设置新房间并标记状态为'changed'
          UPDATE Bookings
          SET room_id = @new_room_id,
              status = 'changed',
              reason = CONCAT('Booking reassigned from room ', v_orig_roomname, ' (ID: ', unavailable_room_id, ') to room ', v_new_roomname, ' (ID: ', @new_room_id, ').')
          WHERE booking_id = v_booking_id;

          -- 插入通知消息：详细说明原预定信息和替换后的房间信息
          INSERT INTO Notifications(user_id, message, notification_action)
          VALUES (v_user_id,
                  CONCAT(
                      'Dear ', v_username, ' (User ID: ', v_user_id, '), ',
                      'due to an issue with your originally booked room ', v_orig_roomname, ' (Room ID: ', unavailable_room_id, '), ',
                      'scheduled on ', v_booking_date, ' from ', v_start_time, ' to ', v_end_time, ', ',
                      'your booking has been successfully reassigned to room ', v_new_roomname, ' (Room ID: ', @new_room_id, ').'
                  ),
                  'reminder');
       ELSE
          -- 如果没有找到合适的替代房间，则更新预定状态为'failed'
          UPDATE Bookings
          SET status = 'failed',
              reason = CONCAT('No suitable replacement room found for room ', v_orig_roomname, ' (ID: ', unavailable_room_id, ') during ', v_booking_date, ' from ', v_start_time, ' to ', v_end_time, '.')
          WHERE booking_id = v_booking_id;

          -- 插入通知消息：详细说明原因及预定取消的情况，提示用户需要重新预定
          INSERT INTO Notifications(user_id, message, notification_action)
          VALUES (v_user_id,
                  CONCAT(
                      'Dear ', v_username, ' (User ID: ', v_user_id, '), ',
                      'due to an issue with your originally booked room ', v_orig_roomname, ' (Room ID: ', unavailable_room_id, '), ',
                      'scheduled on ', v_booking_date, ' from ', v_start_time, ' to ', v_end_time, ', ',
                      'we were unable to find a suitable replacement room matching the required equipment and capacity. ',
                      'As a result, your booking has been cancelled. Please rebook manually if necessary.'
                  ),
                  'cancellation');
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

-- Trigger: After an Issue is inserted, automatically send a notification and update the room status.
CREATE TRIGGER after_issue_insert
AFTER INSERT ON Issues
FOR EACH ROW
BEGIN
    DECLARE v_username VARCHAR(255);
    DECLARE v_roomname VARCHAR(255);

    -- Get the username of the reporter and the room name.
    SELECT username INTO v_username FROM Users WHERE user_id = NEW.added_by;
    SELECT room_name INTO v_roomname FROM Rooms WHERE room_id = NEW.room_id;

    -- Insert a detailed notification message.
    INSERT INTO Notifications (user_id, message, notification_action)
    VALUES (
        NULL,
        CONCAT(
            'Attention: Admin ', v_username,
            ' (ID: ', NEW.added_by,
            ') has reported a new issue for room ', v_roomname,
            ' (Room ID: ', NEW.room_id,
            '). Issue details: ', NEW.issue,
            '. Current status: ', NEW.status, '.'
        ),
        'alert'
    );

    -- Update room status.
    IF NEW.status = 'resolved' THEN
        UPDATE Rooms SET room_status = 0 WHERE room_id = NEW.room_id;
    ELSEIF NEW.status IN ('fault', 'in_maintenance') THEN
        UPDATE Rooms SET room_status = 1 WHERE room_id = NEW.room_id;
    ELSEIF NEW.status = 'severe' THEN
        UPDATE Rooms SET room_status = 2 WHERE room_id = NEW.room_id;
    END IF;
END;
//

-- Trigger: When an Issue is updated, send a status change notification.
CREATE TRIGGER after_issue_update
AFTER UPDATE ON Issues
FOR EACH ROW
BEGIN
    DECLARE v_username VARCHAR(255);
    DECLARE v_roomname VARCHAR(255);

    -- Get the username of the reporter and the room name.
    SELECT username INTO v_username FROM Users WHERE user_id = NEW.added_by;
    SELECT room_name INTO v_roomname FROM Rooms WHERE room_id = NEW.room_id;

    IF NEW.status <> OLD.status THEN
        -- Insert a detailed notification message.
        INSERT INTO Notifications (user_id, message, notification_action)
        VALUES (
            NULL,
            CONCAT(
                'Notice: admin ', v_username,
                ' (ID: ', NEW.added_by,
                ') reported an issue status changed for room ', v_roomname,
                ' (Room ID: ', NEW.room_id,
                ', Issue ID: ', NEW.issue_id,
                '). Status changed from ', OLD.status,
                ' to ', NEW.status, '.'
            ),
            'changed'
        );

        -- Update room status.
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





DELIMITER //

CREATE TRIGGER trg_booking_status_change
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    DECLARE msg VARCHAR(512);
    DECLARE v_username VARCHAR(255);
    DECLARE v_roomname VARCHAR(255);

    -- 查询用户名称和房间名称
    SELECT username INTO v_username FROM Users WHERE user_id = NEW.user_id;
    SELECT room_name INTO v_roomname FROM Rooms WHERE room_id = NEW.room_id;

    IF NEW.status <> OLD.status THEN
        IF NEW.status = 'approved' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'has been approved by the administrator.'
            );
        ELSEIF NEW.status = 'rejected' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'has been rejected by the administrator.'
            );
        ELSEIF NEW.status = 'changed' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'due to room issues, your booking (Booking ID: ', NEW.booking_id, ') originally scheduled for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'has been reallocated to an alternative arrangement.'
            );
        ELSEIF NEW.status = 'pending' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'is now pending. Please wait for admin review.'
            );
        ELSEIF NEW.status = 'canceled' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'your booking(Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, ') has been canceled, ',
                'which was scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, '.'
            );
        ELSEIF NEW.status = 'failed' THEN
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'has failed, possibly due to a room conflict with another booking.'
            );
        ELSE
            SET msg = CONCAT(
                'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
                'the status of your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, '), ',
                'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time, ', ',
                'has been updated to ', NEW.status, '.'
            );
        END IF;

        INSERT INTO Notifications(user_id, message, notification_action)
        VALUES (
            NEW.user_id,
            msg,
            CASE
                WHEN NEW.status = 'approved' THEN 'confirmation'
                WHEN NEW.status = 'rejected' THEN 'rejected'
                WHEN NEW.status = 'changed' THEN 'changed'
                WHEN NEW.status = 'pending' THEN 'reminder'
                WHEN NEW.status = 'canceled' THEN 'cancellation'
                WHEN NEW.status = 'failed' THEN 'failed'
                ELSE 'info'
            END
        );
    END IF;
END //

DELIMITER ;



<<<<<<< HEAD
=======







>>>>>>> feature/email
DELIMITER //

CREATE TRIGGER trg_after_booking_insert
AFTER INSERT ON Bookings
FOR EACH ROW
BEGIN
    DECLARE notif_msg VARCHAR(512);
<<<<<<< HEAD
    DECLARE notif_action ENUM('confirmation', 'reminder', 'cancellation', 'changed', 'failed', 'rejected', 'alert', 'info');

    IF NEW.status = 'pending' THEN
        SET notif_msg = CONCAT('Your booking (ID: ', NEW.booking_id, ') is pending approval.Need to wait for administrator confirmation');
        SET notif_action = 'reminder';
    ELSEIF NEW.status = 'approved' THEN
        SET notif_msg = CONCAT('Your booking (ID: ', NEW.booking_id, ') has been approved. Please arrive at your booked room on time for use.');
        SET notif_action = 'confirmation';
    ELSE
        SET notif_msg = CONCAT('Your booking (ID: ', NEW.booking_id, ') has been added with status ', NEW.status, '.');
=======
    DECLARE v_username VARCHAR(255);
    DECLARE v_roomname VARCHAR(255);
    DECLARE notif_action ENUM('confirmation', 'reminder', 'cancellation', 'changed', 'failed', 'rejected', 'alert', 'info');

    -- 查询用户名称和房间名称
    SELECT username INTO v_username FROM Users WHERE user_id = NEW.user_id;
    SELECT room_name INTO v_roomname FROM Rooms WHERE room_id = NEW.room_id;

    IF NEW.status = 'pending' THEN
        SET notif_msg = CONCAT(
            'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
            'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, ') ',
            'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time,
            ' is now pending. Please wait for admin review.'
        );
        SET notif_action = 'reminder';
    ELSEIF NEW.status = 'approved' THEN
        SET notif_msg = CONCAT(
            'Dear ', v_username, ' (User ID: ', NEW.user_id, '), ',
            'your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, ') ',
            'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time,
            ' has been approved automatically. Please arrive at your reserved room on time.'
        );
        SET notif_action = 'confirmation';
    ELSE
        SET notif_msg = CONCAT(
            'Your booking (Booking ID: ', NEW.booking_id, ') for room ', v_roomname, ' (Room ID: ', NEW.room_id, ') ',
            'scheduled on ', NEW.booking_date, ' from ', NEW.start_time, ' to ', NEW.end_time,
            ' has been added with status "', NEW.status, '".'
        );
>>>>>>> feature/email
        SET notif_action = 'info';
    END IF;

    INSERT INTO Notifications(user_id, message, notification_action)
    VALUES (NEW.user_id, notif_msg, notif_action);
END //

DELIMITER ;

<<<<<<< HEAD
=======




-- 开启事件调度器（如果尚未开启）
SET GLOBAL event_scheduler = ON;

DELIMITER //

CREATE EVENT ev_remove_blacklist_entries
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    DELETE FROM Blacklist
    WHERE end_date = CURDATE()
      AND end_time <= CURTIME();
END;
//

DELIMITER ;
>>>>>>> feature/email
