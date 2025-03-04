
USE `booking_system_db`;
SET SQL_SAFE_UPDATES = 0;

DELETE FROM Rooms;
DELETE FROM Room_availability;

-- 插入房间数据
INSERT INTO Rooms (room_id, room_name, capacity, equipment, location, availability) 
VALUES
(1, 'Room A', 20, 'projector, whiteboard', 'Building A', TRUE),
(2, 'Room B', 10, 'whiteboard', 'Building B', TRUE),
(3, 'Room C', 50, 'projector, speaker', 'Building C', TRUE);


-- 插入 Room A 的可用性数据
INSERT INTO Room_availability (availability_id, room_id, available_begin, available_end, available_date, is_available)
VALUES
(1, 1, '08:00:00', '12:00:00', '2025-03-05', TRUE),  -- Room A's availability on 2025-03-05 from 08:00 to 12:00
(2, 1, '13:00:00', '17:00:00', '2025-03-05', TRUE),  -- Room A's availability on 2025-03-05 from 13:00 to 17:00
(3, 2, '09:00:00', '12:00:00', '2025-03-05', TRUE),  -- Room B's availability on 2025-03-05 from 09:00 to 12:00
(4, 2, '14:00:00', '17:00:00', '2025-03-05', TRUE),  -- Room B's availability on 2025-03-05 from 14:00 to 17:00
(5, 3, '08:00:00', '11:00:00', '2025-03-06', TRUE);  -- Room C's availability on 2025-03-06 from 08:00 to 11:00



-- INSERT INTO Rooms (room_name, capacity, equipment, location, availability) VALUES
-- ('12 English Corridorrooms', 30, '希沃白板', 'DllcsUground floor', TRUE),
-- ('DIICsu 635-multipurpose teaching room', 60, '投影', 'DIICsu six floor', TRUE),
-- ('DIICSU 622-seminar room', 90, '投影', 'DIICSU', TRUE),
-- ('formal meeting room', 14, 'Board room configuration', 'DIICSU Ground Floor', TRUE),
-- ('informal meeting room ', 12, 'Open configuration', 'DIICSU Ground Floor', TRUE),
-- ('DIICSU 634 ', 10, 'Board room configuration', 'DIICSU second Floor', TRUE);




