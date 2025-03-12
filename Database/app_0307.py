#  @version: 3/11/2025
#  @author: Xin Yu, Siyan Guo, Zibang Nie
# add: cancel a booking,approve or reject a booking



from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # 允许所有来源访问

# ---------------------------- 数据库连接配置 ----------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",  # 注意：删除操作中使用的是1234，请保持一致
    "database": "booking_system_db"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# ---------------------------- 删除操作的辅助函数 ----------------------------
def delete_record(query, params):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return "Deletion successful.", 200
    except Exception as e:
        conn.rollback()
        return f"Error occurred: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()

# ---------------------------- 其他辅助函数 ----------------------------
def validate_time(time_str):
    """验证时间格式 HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def format_time(time_val):
    """
    将时间或 timedelta 对象转化为 HH:MM 格式字符串
    如果 time_val 为 datetime.time 类型，则直接转换为字符串
    """
    if isinstance(time_val, timedelta):
        total_seconds = int(time_val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    try:
        return time_val.strftime("%H:%M")
    except Exception:
        return str(time_val)

def generate_date_range(start_date, end_date):
    """生成从 start_date 到 end_date（含）之间的所有日期列表"""
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list

def get_room_id(room_name):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT room_id FROM Rooms WHERE room_name = %s", (room_name,))
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        if conn:
            conn.close()

# ---------------------------- 删除操作接口 ----------------------------
@app.route('/delete/users', methods=['POST'])
def delete_users():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    role = data.get('role')
    # 使用同一数据库连接和事务，先删除依赖于该用户的记录，再删除用户记录
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if user_id:
            # 1. 删除该用户的通知记录
            cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
            # 2. 删除该用户预订的记录，其审批记录依赖于预订（先删除审批记录）
            cursor.execute("""
                DELETE FROM Approvals 
                WHERE booking_id IN (
                    SELECT booking_id FROM Bookings WHERE user_id = %s
                )
            """, (user_id,))
            # 删除该用户的预订记录
            cursor.execute("DELETE FROM Bookings WHERE user_id = %s", (user_id,))
            # 3. 删除审批记录中，该用户作为管理员审批的记录
            cursor.execute("DELETE FROM Approvals WHERE admin_id = %s", (user_id,))
            # 4. 删除该用户生成的报告
            cursor.execute("DELETE FROM Reports WHERE admin_id = %s", (user_id,))
        # 删除用户记录
        query = """
        DELETE FROM Users
        WHERE (user_id = %s OR %s IS NULL)
          AND (username = %s OR %s IS NULL)
          AND (email = %s OR %s IS NULL)
          AND (role = %s OR %s IS NULL)
        """
        params = (user_id, user_id, username, username, email, email, role, role)
        cursor.execute(query, params)
        conn.commit()
        result = "Deletion successful."
        status_code = 200
    except Exception as e:
        conn.rollback()
        result = f"Error occurred: {str(e)}"
        status_code = 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": result}), status_code

@app.route('/delete/rooms', methods=['POST'])
def delete_rooms():
    data = request.json
    room_id = data.get('room_id')
    room_name = data.get('room_name')
    capacity = data.get('capacity')
    location = data.get('location')
    # 先删除依赖数据：Room_availability、Bookings（依赖该房间）
    dependent_queries = [
        ("DELETE FROM Room_availability WHERE room_id = %s", (room_id,)),
        ("DELETE FROM Bookings WHERE room_id = %s", (room_id,))
    ]
    for q, p in dependent_queries:
        delete_record(q, p)
    query = """
    DELETE FROM Rooms
    WHERE (room_id = %s OR %s IS NULL)
      AND (room_name = %s OR %s IS NULL)
      AND (capacity = %s OR %s IS NULL)
      AND (location = %s OR %s IS NULL)
    """
    params = (room_id, room_id, room_name, room_name, capacity, capacity, location, location)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/room_availability', methods=['POST'])
def delete_room_availability():
    data = request.json
    room_id = data.get('room_id')
    available_date = data.get('available_date')
    available_begin = data.get('available_begin')
    available_end = data.get('available_end')
    query = """
    DELETE FROM Room_availability
    WHERE (room_id = %s OR %s IS NULL)
      AND (available_date = %s OR %s IS NULL)
      AND (available_begin = %s OR %s IS NULL)
      AND (available_end = %s OR %s IS NULL)
    """
    params = (room_id, room_id, available_date, available_date, available_begin, available_begin, available_end, available_end)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

# @app.route('/delete/bookings', methods=['POST', 'OPTIONS'])
# def delete_bookings():
#     if request.method == 'OPTIONS':
#         return '', 200
#     data = request.json
#     booking_id = data.get('booking_id')
#     start_time = data.get('start_time')
#     end_time = data.get('end_time')
#     booking_date = data.get('booking_date')
#     status_val = data.get('status')
#     # 删除依赖记录：审批记录中对应的 booking_id
#     dependent_query = """
#     DELETE FROM Approvals
#     WHERE booking_id = %s
#     """
#     dependent_params = (booking_id,)
#     delete_record(dependent_query, dependent_params)
#     # 根据 booking_id 及其他参数删除 Bookings 中的记录
#     query = """
#     DELETE FROM Bookings
#     WHERE booking_id = %s
#       AND start_time = %s
#       AND end_time = %s
#       AND booking_date = %s
#       AND (status = %s OR %s IS NULL)
#     """
#     params = (booking_id, start_time, end_time, booking_date, status_val, status_val)
#     result, status = delete_record(query, params)
#     return jsonify({"message": result}), status

@app.route('/delete/approvals', methods=['POST'])
def delete_approvals():
    data = request.json
    approval_id = data.get('approval_id')
    booking_id = data.get('booking_id')
    admin_id = data.get('admin_id')
    approval_status = data.get('approval_status')
    query = """
    DELETE FROM Approvals
    WHERE (approval_id = %s OR %s IS NULL)
      AND (booking_id = %s OR %s IS NULL)
      AND (admin_id = %s OR %s IS NULL)
      AND (approval_status = %s OR %s IS NULL)
    """
    params = (approval_id, approval_id, booking_id, booking_id, admin_id, admin_id, approval_status, approval_status)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/notifications', methods=['POST'])
def delete_notifications():
    data = request.json
    notification_id = data.get('notification_id')
    user_id = data.get('user_id')
    notification_type = data.get('notification_type')
    status_val = data.get('status')
    query = """
    DELETE FROM Notifications
    WHERE (notification_id = %s OR %s IS NULL)
      AND (user_id = %s OR %s IS NULL)
      AND (notification_type = %s OR %s IS NULL)
      AND (status = %s OR %s IS NULL)
    """
    params = (notification_id, notification_id, user_id, user_id, notification_type, notification_type, status_val, status_val)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/reports', methods=['POST'])
def delete_reports():
    data = request.json
    report_id = data.get('report_id')
    admin_id = data.get('admin_id')
    report_type = data.get('report_type')
    query = """
    DELETE FROM Reports
    WHERE (report_id = %s OR %s IS NULL)
      AND (admin_id = %s OR %s IS NULL)
      AND (report_type = %s OR %s IS NULL)
    """
    params = (report_id, report_id, admin_id, admin_id, report_type, report_type)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/notifications_by_user', methods=['POST'])
def delete_notifications_by_user():
    data = request.json
    user_id = data.get('user_id')
    query = "DELETE FROM Notifications WHERE user_id = %s"
    params = (user_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/approvals_by_booking', methods=['POST'])
def delete_approvals_by_booking():
    data = request.json
    booking_id = data.get('booking_id')
    query = "DELETE FROM Approvals WHERE booking_id = %s"
    params = (booking_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

@app.route('/delete/room_availability_by_room', methods=['POST'])
def delete_room_availability_by_room():
    data = request.json
    room_id = data.get('room_id')
    query = "DELETE FROM Room_availability WHERE room_id = %s"
    params = (room_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

# ---------------------------- search/display ----------------------------

@app.route('/search-rooms', methods=['POST'])
def search_rooms():
    """
    请求参数示例：
    {

        "capacity": 20,
        "room_name": "会议室",
        "date": "2025-03-05",
        "start_time": "08:00",
        "end_time": "12:00",
        "equipment": "projector"
    }
    所有参数均为可选，可以任意组合
    """
    params = request.json or {}
    capacity = params.get('capacity')
    room_name = params.get('room_name')
    date = params.get('date')
    start_time = params.get('start_time')
    end_time = params.get('end_time')
    equipment = params.get('equipment')

    if start_time and not validate_time(start_time):
        return jsonify({"error": "Invalid start_time format (HH:MM)"}), 400
    if end_time and not validate_time(end_time):
        return jsonify({"error": "Invalid end_time format (HH:MM)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = """
            SELECT 
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,r.is_normal_Room,
                ra.available_date, ra.available_begin, ra.available_end, ra.availability
            FROM Rooms r
            JOIN Room_availability ra ON r.room_id = ra.room_id
            WHERE ra.availability IN (0, 2)
        """
        query_params = []
        if capacity:
            query += " AND r.capacity >= %s"
            query_params.append(int(capacity))
        if room_name:
            query += " AND r.room_name LIKE %s"
            query_params.append(f"%{room_name}%")
        if date:
            formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
            query += " AND DATE(ra.available_date) = %s"
            query_params.append(formatted_date)
        if start_time:
            query += " AND ra.available_begin >= %s"
            query_params.append(f"{start_time}:00")
        if end_time:
            query += " AND ra.available_end <= %s"
            query_params.append(f"{end_time}:00")
        if equipment:
            query += " AND r.equipment LIKE %s"
            query_params.append(f"%{equipment}%")

        print("[调试] 最终SQL:", query)
        print("[调试] 参数:", query_params)

        cursor.execute(query, query_params)
        results = cursor.fetchall()

        for result in results:
            result['available_begin'] = format_time(result['available_begin'])
            result['available_end'] = format_time(result['available_end'])

        return jsonify({
            "count": len(results),
            "results": results
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/bookings', methods=['GET'])
def get_all_bookings():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time, b.status,
                r.room_name, r.location, r.capacity, r.equipment
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            ORDER BY b.booking_date, b.start_time
        """
        cursor.execute(query)
        bookings = cursor.fetchall()
        for booking in bookings:
            booking['start_time'] = format_time(booking['start_time'])
            booking['end_time'] = format_time(booking['end_time'])
            booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")
        return jsonify({
            "count": len(bookings),
            "bookings": bookings
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT room_id, room_name, capacity, equipment, location
            FROM Rooms
        """
        cursor.execute(query)
        rooms = cursor.fetchall()
        return jsonify({
            "count": len(rooms),
            "rooms": rooms
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/pending-bookings', methods=['GET'])
def get_pending_bookings():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL 查询，获取状态为 'pending' 的预定记录，并连接 Users 和 Rooms 表
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,
                u.username AS user_name, r.room_name
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.status = 'pending'
            ORDER BY b.booking_date, b.start_time
        """

        # 执行查询
        cursor.execute(query)
        bookings = cursor.fetchall()

        # 格式化返回的数据
        for booking in bookings:
            booking['start_time'] = format_time(booking['start_time'])
            booking['end_time'] = format_time(booking['end_time'])
            booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")

        # 返回数据
        return jsonify({
            "count": len(bookings),
            "bookings": bookings
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/approved-bookings', methods=['GET'])
def get_approved_bookings():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL 查询，获取状态为 'pending' 的预定记录，并连接 Users 和 Rooms 表
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,
                u.username AS user_name, r.room_name
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.status = 'approved'
            ORDER BY b.booking_date, b.start_time
        """

        # 执行查询
        cursor.execute(query)
        bookings = cursor.fetchall()

        # 格式化返回的数据
        for booking in bookings:
            booking['start_time'] = format_time(booking['start_time'])
            booking['end_time'] = format_time(booking['end_time'])
            booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")

        # 返回数据
        return jsonify({
            "count": len(bookings),
            "bookings": bookings
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ---------------------------- update ----------------------------

@app.route('/update-room/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    print(f"Received PUT request to update room with ID: {room_id}")
    data = request.json
    print(f"Request body: {data}")
    room_name = data.get('room_name')
    capacity = data.get('capacity')
    equipment = data.get('equipment')
    location = data.get('location')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
        existing_room = cursor.fetchone()
        if existing_room:
            print(f"Room name '{room_name}' already exists.")
            return jsonify({"error": "Room name already exists"}), 400
        update_query = """
            UPDATE Rooms
            SET room_name = %s, capacity = %s, equipment = %s, location = %s
            WHERE room_id = %s
        """
        update_params = (room_name, capacity, equipment, location, room_id)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()
        if cursor.rowcount == 0:
            print(f"No room found with ID {room_id}.")
            return jsonify({"error": "Room not found"}), 404
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        updated_room = cursor.fetchone()
        print(f"Updated room: {updated_room}")
        return jsonify({
            "message": "Room updated successfully",
            "room_id": updated_room[0],
            "room_name": updated_room[1],
            "capacity": updated_room[2],
            "equipment": updated_room[3],
            "location": updated_room[4]
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/update-booking-status/<int:booking_id>', methods=['PUT'])
def update_booking_status(booking_id):
    print(f"Received PUT request to update booking with ID: {booking_id}")
    data = request.json
    print(f"Request body: {data}")
    status = data.get('status')

    if status not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status value. Allowed values are 'approved' or 'rejected'."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the booking exists and is in 'pending' status
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s AND status = 'pending'", (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            print(f"No pending booking found with ID {booking_id}.")
            return jsonify({"error": "Booking not found or already processed"}), 404

        # Update the booking's status
        update_query = """
            UPDATE Bookings
            SET status = %s
            WHERE booking_id = %s
        """
        update_params = (status, booking_id)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()

        if cursor.rowcount == 0:
            print(f"No room found with ID {booking_id}.")
            return jsonify({"error": "Booking update failed"}), 500

        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        return jsonify({
            "message": f"Booking status updated to {status}",
            "booking_id": updated_booking[0],
            "status": updated_booking[6]  # Assuming status is the 6th column in Bookings table
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@app.route('/cancel-booking/<int:booking_id>', methods=['PUT'])
def cancel_booking(booking_id):
    print(f"Received PUT request to cancel booking with ID: {booking_id}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 查找待取消的预定记录
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s AND status != 'canceled'", (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            print(f"No booking found with ID {booking_id} or the booking is already canceled.")
            return jsonify({"error": "Booking not found or already canceled"}), 404

        # 更新该预定的 status 为 'canceled'
        update_query = """
            UPDATE Bookings
            SET status = 'canceled'
            WHERE booking_id = %s
        """
        update_params = (booking_id,)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()

        if cursor.rowcount == 0:
            print(f"Failed to cancel booking with ID {booking_id}.")
            return jsonify({"error": "Failed to cancel booking"}), 500

        # 获取更新后的预定信息
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        return jsonify({
            "message": "Booking status updated to 'canceled'",
            "booking_id": updated_booking[0],
            "status": updated_booking[6]  # Assuming status is the 6th column in Bookings table
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()



# ---------------------------- insert ----------------------------

@app.route('/insert_booking', methods=['POST'])
def insert_booking():
    data = request.get_json()
    # 获取房间名称并转换为ID
    room_name = data['room_name']
    room_id = get_room_id(room_name)
    if not room_id:
        return jsonify({
            "status": "error",
            "error": f"Room '{room_name}' does not exist"
        }), 400
    user_id = data['user_id']
    booking_date = data['booking_date']
    start_time = data['start_time'] + ":00"
    end_time = data['end_time'] + ":00"
    status = 'approved'
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, room_id, start_time, end_time, booking_date, status))
        conn.commit()
        return jsonify({"status": "success", "message": "Booking inserted successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()

@app.route('/insert_room', methods=['POST'])
def insert_room():
    data = request.get_json()
    room_name = data['room_name']
    capacity = data['capacity']
    equipment = data['equipment']
    location = data['location']
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Rooms (room_name, capacity, equipment, location)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (room_name, capacity, equipment, location))
        conn.commit()
        return jsonify({"status": "success", "message": "Room inserted successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()



if __name__ == '__main__':
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"→ {rule}")
    app.run(debug=True)
