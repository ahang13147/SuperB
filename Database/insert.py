# version 1.4

from flask import Flask, render_template, request, jsonify  # 新增 jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 数据库配置（根据你的MySQL信息修改）
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "0000",  # 替换为你的密码
    "database": "booking_system_db"
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None
    
# 新增查询房间ID的函数
def get_room_id(room_name):
    conn = get_db_connection()
    if not conn:
        return None
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
 

@app.route('/booking')
def booking():
    return render_template('booking_form.html')

@app.route('/insert_booking', methods=['POST'])
def insert_booking():
    
    data = request.get_json()
    """
    创建新预约的接口
    请求参数示例：
    {
        "room_name": "会议室1",     // 必须，会议室名称
        "user_id": 1,             // 必须，用户ID
        "booking_date": "2025-03-05",  // 必须，预约日期
        "start_time": "08:00",   // 必须，开始时间（HH:MM格式）
        "end_time": "10:00"       // 必须，结束时间（HH:MM格式）
    }
    前端调用示例：
    fetch('http://localhost:5000/insert_booking', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_name: "会议室1",
            user_id: 1,
            booking_date: "2025-03-05",
            start_time: "08:00",
            end_time: "10:00"
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
    """
    # 获取房间名称并转换为ID
    room_name = data['room_name']
    room_id = get_room_id(room_name)
    if not room_id:
        return jsonify({
            "status": "error",
            "error": f"Room '{room_name}' does not exist"
        }), 400

    # 其他字段保持不变
    user_id = data['user_id']
    booking_date = data['booking_date']
    start_time = data['start_time'] + ":00"
    end_time = data['end_time'] + ":00"
    # status = data['status']
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

@app.route('/')
def index():
    return render_template('room_form.html')

@app.route('/insert_room', methods=['POST'])
def insert_room():
    """
    创建新会议室的接口
    请求参数示例：
    {
        "room_name": "新会议室",  // 必须，会议室名称
        "capacity": 30,         // 必须，容纳人数
        "equipment": "投影仪,白板", // 设备列表
        "location": "3楼东侧"    // 位置信息
    }
    前端调用示例：
    fetch('http://localhost:5000/insert_room', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            room_name: "新会议室",
            capacity: 30,
            equipment: "投影仪,白板",
            location: "3楼东侧"
        })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error:', error));
    """
    data = request.get_json()
    # 移除了 availability 字段
    room_name = data['room_name']
    capacity = data['capacity']
    equipment = data['equipment']
    location = data['location']

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()
        # 修改 SQL 语句，移除 availability
        query = """
        INSERT INTO Rooms (room_name, capacity, equipment, location)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (room_name, capacity, equipment, location))  # 参数减少为 4 个
        conn.commit()
        return jsonify({"status": "success", "message": "Room inserted successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)