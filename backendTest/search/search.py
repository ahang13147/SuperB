from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# 数据库配置
db_config = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "booking_system_db"
}


def get_db_connection():
    return mysql.connector.connect(**db_config)


def validate_time(time_str):
    """验证时间格式 HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


# 将 timedelta 对象转化为 HH:MM 格式字符串
def format_time(timedelta_obj):
    if isinstance(timedelta_obj, timedelta):
        total_seconds = int(timedelta_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    return timedelta_obj


@app.route('/search-rooms', methods=['POST'])
def search_rooms():
    """
    请求参数示例：
    {
        "capacity": 20,          // 可选，>= 值
        "room_name": "会议室",    // 可选，模糊匹配
        "date": "2025-03-05",    // 可选，精确匹配
        "start_time": "08:00",   // 可选，HH:MM 格式
        "end_time": "12:00"      // 可选，HH:MM 格式
    }
    所有参数均为可选，可以任意组合
    """
    # 获取参数
    params = request.json or {}
    capacity = params.get('capacity')
    room_name = params.get('room_name')
    date = params.get('date')
    start_time = params.get('start_time')
    end_time = params.get('end_time')
    equipment = params.get('equipment')

    # 参数验证
    if start_time and not validate_time(start_time):
        return jsonify({"error": "Invalid start_time format (HH:MM)"}), 400
    if end_time and not validate_time(end_time):
        return jsonify({"error": "Invalid end_time format (HH:MM)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 构建基础查询
        query = """
            SELECT 
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,
                ra.available_date, ra.available_begin, ra.available_end
            FROM Rooms r
            JOIN Room_availability ra ON r.room_id = ra.room_id
            WHERE 1=1
        """
        query_params = []

        # 动态添加条件
        if capacity:
            query += " AND r.capacity >= %s"
            query_params.append(int(capacity))

        if room_name:
            query += " AND r.room_name LIKE %s"
            query_params.append(f"%{room_name}%")

        if date:
            # 确保数据库中的 available_date 被转换为只含日期的格式
            formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
            query += " AND DATE(ra.available_date) = %s"
            query_params.append(formatted_date)

        if start_time:
            query += " AND ra.available_begin <= %s"
            query_params.append(f"{start_time}:00")

        if end_time:
            query += " AND ra.available_end >= %s"
            query_params.append(f"{end_time}:00")
        # 新增设备条件
        if equipment:
            query += " AND r.equipment LIKE %s"
            query_params.append(f"%{equipment}%")

        # 执行查询
        cursor.execute(query, query_params)
        results = cursor.fetchall()

        # 格式化时间字段
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


if __name__ == '__main__':
    app.run(debug=True)
