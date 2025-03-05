from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime, timedelta, date, time  # 新增必要类型导入

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


def format_timedelta(td):
    """将 timedelta 转换为 HH:MM:SS 字符串"""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


@app.route('/search-rooms', methods=['POST'])
def search_rooms():
    """
    请求参数示例：
    {
        "capacity": 20,          // 可选，>= 值
        "equipment": "投影仪",   // 可选，模糊匹配
        "date": "2025-03-05",    // 可选，精确匹配
        "start_time": "08:00",   // 可选，HH:MM 格式
        "end_time": "12:00"      // 可选，HH:MM 格式
    }
    """
    params = request.json or {}
    capacity = params.get('capacity')
    equipment = params.get('equipment')
    date_param = params.get('date')
    start_time = params.get('start_time')
    end_time = params.get('end_time')

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
                r.room_id,
                r.room_name,
                r.capacity,
                r.equipment,
                r.location,
                ra.available_date,
                ra.available_begin,
                ra.available_end
            FROM Rooms r
            JOIN Room_availability ra ON r.room_id = ra.room_id
            WHERE 1=1
        """
        query_params = []

        # 动态添加条件
        if capacity:
            query += " AND r.capacity >= %s"
            query_params.append(int(capacity))

        if equipment:
            query += " AND r.equipment LIKE %s"
            query_params.append(f"%{equipment}%")

        if date_param:
            query += " AND ra.available_date = %s"
            query_params.append(date_param)

        if start_time:
            query += " AND ra.available_begin <= %s"
            query_params.append(f"{start_time}:00")

        if end_time:
            query += " AND ra.available_end >= %s"
            query_params.append(f"{end_time}:00")

        # 调试输出
        print("[执行SQL]", query)
        print("[查询参数]", query_params)

        cursor.execute(query, query_params)
        raw_results = cursor.fetchall()

        # 格式化结果
        formatted_results = []
        for item in raw_results:
            # 处理日期字段
            if isinstance(item['available_date'], date):
                item['available_date'] = item['available_date'].strftime("%Y-%m-%d")

            # 处理开始时间字段
            if isinstance(item['available_begin'], timedelta):
                item['available_begin'] = format_timedelta(item['available_begin'])
            elif isinstance(item['available_begin'], time):
                item['available_begin'] = item['available_begin'].strftime("%H:%M:%S")

            # 处理结束时间字段
            if isinstance(item['available_end'], timedelta):
                item['available_end'] = format_timedelta(item['available_end'])
            elif isinstance(item['available_end'], time):
                item['available_end'] = item['available_end'].strftime("%H:%M:%S")

            formatted_results.append(item)

        return jsonify({
            "count": len(formatted_results),
            "results": formatted_results
        })

    except mysql.connector.Error as e:
        print(f"数据库错误: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print(f"系统错误: {str(e)}", exc_info=True)  # 打印完整堆栈信息
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)