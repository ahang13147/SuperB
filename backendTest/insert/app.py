from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/')
def index():
    return render_template('room_form.html')

@app.route('/insert_room', methods=['POST'])
def insert_room():
    # 获取表单数据
    room_name = request.form['room_name']
    capacity = request.form['capacity']
    equipment = request.form['equipment']
    location = request.form['location']
    availability = request.form['availability'] == 'true'

    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return render_template('room_form.html', error="Database connection failed")

    try:
        cursor = conn.cursor()
        # 执行插入操作（使用参数化查询防止SQL注入）
        query = """
        INSERT INTO Rooms (room_name, capacity, equipment, location, availability)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (room_name, capacity, equipment, location, availability))
        conn.commit()
        return render_template('room_form.html', message="Room inserted successfully!")
    except mysql.connector.Error as err:
        conn.rollback()
        return render_template('room_form.html', error=f"Error: {err}")
    finally:
        if conn:
            conn.close()

@app.route('/booking')
def booking():
    return render_template('booking_form.html')

@app.route('/insert_booking', methods=['POST'])
def insert_booking():
    # 获取表单数据
    user_id = request.form['user_id']
    room_id = request.form['room_id']
    booking_date = request.form['booking_date']  # 获取 booking_date
    start_time = request.form['start_time']  # 获取 start_time (HH:MM)
    end_time = request.form['end_time']  # 获取 end_time (HH:MM)
    status = request.form['status']

    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return render_template('booking_form.html', error="Database connection failed")

    try:
        cursor = conn.cursor()
        # 执行插入操作（使用参数化查询防止SQL注入）
        query = """
        INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        # 将时间格式化为 HH:MM:SS
        start_time_formatted = f"{start_time}:00"
        end_time_formatted = f"{end_time}:00"
        cursor.execute(query, (user_id, room_id, start_time_formatted, end_time_formatted, booking_date, status))
        conn.commit()
        return render_template('booking_form.html', message="Booking inserted successfully!")
    except mysql.connector.Error as err:
        conn.rollback()
        return render_template('booking_form.html', error=f"Error: {err}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)