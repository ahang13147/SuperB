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
    "password": "1234",  # 替换为你的数据库密码
    "database": "booking_system_db"
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

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

# ---------------------------- 删除 Users ----------------------------
@app.route('/delete/users', methods=['POST'])
def delete_users():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    role = data.get('role')
    # 使用同一数据库连接和事务，先删除依赖记录，再删除用户
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if user_id:
            # 先删除依赖数据：通知、预订、审批（admin_id）和报告（admin_id）
            cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM Bookings WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM Approvals WHERE admin_id = %s", (user_id,))
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

# ---------------------------- 删除 Rooms ----------------------------
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

# ---------------------------- 删除 Room_availability ----------------------------
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

# ---------------------------- 删除 Bookings ----------------------------
@app.route('/delete/bookings', methods=['POST'])
def delete_bookings():
    data = request.json
    # 根据 room_name 来查找 room_id，再加上 start_time, end_time, booking_date, status
    room_name = data.get('room_name')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    booking_date = data.get('booking_date')
    status_val = data.get('status')
    # 先删除依赖：审批记录对应的 booking_id
    dependent_query = """
    DELETE FROM Approvals 
    WHERE booking_id IN (
        SELECT booking_id FROM Bookings 
        WHERE room_id = (SELECT room_id FROM Rooms WHERE room_name = %s)
          AND start_time = %s
          AND end_time = %s
          AND booking_date = %s
          AND (status = %s OR %s IS NULL)
    )
    """
    dependent_params = (room_name, start_time, end_time, booking_date, status_val, status_val)
    delete_record(dependent_query, dependent_params)
    query = """
    DELETE FROM Bookings
    WHERE room_id = (SELECT room_id FROM Rooms WHERE room_name = %s)
      AND start_time = %s
      AND end_time = %s
      AND booking_date = %s
      AND (status = %s OR %s IS NULL)
    """
    params = (room_name, start_time, end_time, booking_date, status_val, status_val)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status

# ---------------------------- 删除 Approvals ----------------------------
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

# ---------------------------- 删除 Notifications ----------------------------
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

# ---------------------------- 删除 Reports ----------------------------
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

# ---------------------------- 针对外键删除的额外接口 ----------------------------
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

if __name__ == '__main__':
    app.run(debug=True)
