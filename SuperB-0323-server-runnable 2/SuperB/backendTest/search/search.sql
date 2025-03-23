USE `booking_system_db`;

SELECT r.room_id, r.room_name, r.capacity, r.equipment, r.location, ra.available_date, ra.available_begin, ra.available_end
FROM Rooms r
JOIN Room_availability ra ON r.room_id = ra.room_id
WHERE (r.capacity >= IFNULL(?, r.capacity))  -- 如果没有提供容量，则不限制
  AND (r.equipment LIKE IFNULL(?, r.equipment))  -- 如果没有提供设备，则不限制
  AND (ra.available_date = IFNULL(?, ra.available_date))  -- 如果没有提供日期，则不限制
  AND (ra.available_begin <= IFNULL(?, ra.available_begin))  -- 如果没有提供开始时间，则不限制
  AND (ra.available_end >= IFNULL(?, ra.available_end));  -- 如果没有提供结束时间，则不限制

