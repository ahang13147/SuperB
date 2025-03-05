from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "0000",
    "database": "booking_system_db"
}

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def process_value(value, data_type):
    """根据数据类型处理值"""
    if data_type in ['tinyint', 'boolean']:
        return 1 if value.lower() == 'true' else 0
    elif data_type == 'time' and len(value) == 5:
        return f"{value}:00"
    elif data_type in ['int', 'integer', 'smallint', 'mediumint', 'bigint']:
        return int(value) if value.isdigit() else value
    return value

@app.route('/')
def index():
    return render_template('room_form.html')

@app.route('/booking')
def booking():
    return render_template('booking_form.html')

@app.route('/insert', methods=['POST'])
def dynamic_insert():
    table = request.form.get('table')
    if not table:
        return render_template('error.html', error="Table name required")

    conn = get_db_connection()
    if not conn:
        return render_template('error.html', error="Database connection failed")

    try:
        cursor = conn.cursor()
        
        # 验证表是否存在
        cursor.execute("SHOW TABLES LIKE %s", (table,))
        if not cursor.fetchone():
            raise ValueError(f"Table {table} does not exist")

        # 获取列元数据
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [col[0] for col in cursor.fetchall()]
        form_data = {k: v for k, v in request.form.items() if k != 'table' and k in columns}

        # 类型转换
        cursor.execute(f"DESCRIBE {table}")
        type_info = {col[0]: col[1] for col in cursor.fetchall()}
        processed_data = {}
        for col, val in form_data.items():
            data_type = type_info[col].split('(')[0].lower()
            processed_data[col] = process_value(val, data_type)

        # 构建并执行查询
        query = f"INSERT INTO {table} ({', '.join(processed_data.keys())}) VALUES ({', '.join(['%s']*len(processed_data))})"
        cursor.execute(query, list(processed_data.values()))
        conn.commit()

        template = 'room_form.html' if table == 'Rooms' else 'booking_form.html'
        return render_template(template, message=f"Data inserted into {table} successfully!")
    
    except Exception as e:
        conn.rollback()
        template = 'room_form.html' if table == 'Rooms' else 'booking_form.html'
        return render_template(template, error=str(e))
    finally:
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True)