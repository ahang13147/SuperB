from flask import Flask, render_template, request
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
    return render_template('booking_form.html')

@app.route('/insert', methods=['POST'])
def insert_booking():
    # 获取表单数据
    user_id = request.form['user_id']
    room_id = request.form['room_id']
    start_time = request.form['start_time'].replace('T', ' ') + ':00'
    end_time = request.form['end_time'].replace('T', ' ') + ':00'
    status = request.form['status']

    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return render_template('booking_form.html', error="Database connection failed")

    try:
        cursor = conn.cursor()
        # 执行插入操作（使用参数化查询防止SQL注入）
        query = """
        INSERT INTO Bookings (user_id, room_id, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, room_id, start_time, end_time, status))
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