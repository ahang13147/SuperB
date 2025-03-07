from flask import Flask, request, jsonify
from flask_cors import CORS  # 导入 CORS 模块
import pymysql
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)  # 启用 CORS，允许所有域名的请求

# 数据库连接配置，请根据实际情况修改
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'booking_system_db',
    'charset': 'utf8mb4'
}

# 预定义的时间段列表，每个字符串格式为 "开始时间-结束时间"
time_slots = [
    "08:00-08:45",
    "08:55-09:40",
    "10:00-10:45",
    "10:55-11:40",
    "14:00-14:45",
    "14:55-15:40",
    "16:00-16:45",
    "16:55-17:40",
    "19:00-19:45",
    "19:55-20:40"
]

def generate_date_range(start_date, end_date):
    """生成从 start_date 到 end_date（含）之间的所有日期列表"""
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list

@app.route('/create_room_availability', methods=['POST'])
def create_room_availability():
    data = request.get_json()
    if not data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({'error': '必须传入 start_date 与 end_date，格式为 yyyy-mm-dd'}), 400

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': '日期格式错误，应为 yyyy-mm-dd'}), 400

    if start_date > end_date:
        return jsonify({'error': 'start_date 不能大于 end_date'}), 400

    date_range = generate_date_range(start_date, end_date)
    inserted_records = 0
    updated_records = 0

    # 连接数据库
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 查询所有房间记录
            cursor.execute("SELECT room_id, room_name FROM Rooms")
            rooms = cursor.fetchall()
            if not rooms:
                return jsonify({'error': '未查询到房间记录'}), 404

            # 针对每个房间，每个日期，每个时间段插入或更新记录
            for room in rooms:
                room_id = room[0]  # 假定第一列为 room_id
                for current_date in date_range:
                    for slot in time_slots:
                        start_time_str, end_time_str = slot.split('-')
                        # 检查是否已存在相同 room_id, available_begin, available_end, available_date 的记录
                        select_sql = """
                            SELECT availability_id FROM Room_availability
                            WHERE room_id = %s AND available_begin = %s AND available_end = %s AND available_date = %s
                        """
                        cursor.execute(select_sql, (room_id, start_time_str, end_time_str, current_date))
                        result = cursor.fetchone()
                        if result:
                            # 记录已存在，更新记录（覆盖）
                            availability_id = result[0]
                            update_sql = """
                                UPDATE Room_availability
                                SET availability = %s
                                WHERE availability_id = %s
                            """
                            cursor.execute(update_sql, (0, availability_id))
                            updated_records += 1
                        else:
                            # 记录不存在，插入新记录
                            insert_sql = """
                                INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability)
                                VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(insert_sql, (room_id, start_time_str, end_time_str, current_date, 0))
                            inserted_records += 1
            connection.commit()
    except Exception as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()

    return jsonify({
        'message': '房间可用时间生成成功（已覆盖重复记录）',
        'inserted_records': inserted_records,
        'updated_records': updated_records
    })

if __name__ == '__main__':
    app.run(debug=True)
