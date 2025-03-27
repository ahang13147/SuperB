# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# from datetime import datetime, timedelta
#
# app = Flask(__name__)
# CORS(app)
#
# # 数据库配置
# db_config = {
#     "host": "localhost",
#     "port": 3306,
#     "user": "root",
#     "password": "1234",
#     "database": "booking_system_db"
# }
#
#
# def get_db_connection():
#     return mysql.connector.connect(**db_config)
#
#
# def validate_time(time_str):
#     """验证时间格式 HH:MM"""
#     try:
#         datetime.strptime(time_str, "%H:%M")
#         return True
#     except ValueError:
#         return False
#
#
# # 将 timedelta 对象转化为 HH:MM 格式字符串
# def format_time(timedelta_obj):
#     if isinstance(timedelta_obj, timedelta):
#         total_seconds = int(timedelta_obj.total_seconds())
#         hours = total_seconds // 3600
#         minutes = (total_seconds % 3600) // 60
#         return f"{hours:02}:{minutes:02}"
#     return timedelta_obj
#
#
# @app.route('/search-rooms', methods=['POST'])
# def search_rooms():
#     """
#     请求参数示例：
#     const requestData = {
#         "capacity": 20,          // 可选，>= 值
#         "room_name": "会议室",    // 可选，模糊匹配
#         "date": "2025-03-05",    // 可选，精确匹配
#         "start_time": "08:00",   // 可选，HH:MM 格式
#         "end_time": "12:00"      // 可选，HH:MM 格式
#         "equipment": "projector" //可选
#     }
#     所有参数均为可选，可以任意组合
#     // 发送POST请求
# fetch('https://101.200.197.132:5000/search-rooms', {
#     method: 'POST',
#     headers: {
#         'Content-Type': 'application/json'  // 设置请求头为JSON
#     },
#     body: JSON.stringify(requestData)  // 将请求体转为JSON字符串
# })
# .then(response => response.json())  // 解析返回的JSON数据
# .then(data => {
#     console.log('Response:', data);  // 打印返回的数据
# })
# .catch(error => {
#     console.error('Error:', error);  // 错误处理
# });
#     """
#     # 获取参数
#     params = request.json or {}
#     capacity = params.get('capacity')
#     room_name = params.get('room_name')
#     date = params.get('date')
#     start_time = params.get('start_time')
#     end_time = params.get('end_time')
#     equipment = params.get('equipment')
#
#     # 参数验证
#     if start_time and not validate_time(start_time):
#         return jsonify({"error": "Invalid start_time format (HH:MM)"}), 400
#     if end_time and not validate_time(end_time):
#         return jsonify({"error": "Invalid end_time format (HH:MM)"}), 400
#
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True, buffered=True)  # 添加buffered=True
#
#         # 构建基础查询
#         query = """
#             SELECT
#                 r.room_id, r.room_name, r.capacity, r.equipment, r.location,
#                 ra.available_date, ra.available_begin, ra.available_end, ra.availability
#             FROM Rooms r
#             JOIN Room_availability ra ON r.room_id = ra.room_id
#             WHERE ra.availability IN (0, 2)
#         """
#         query_params = []
#
#         # 动态添加条件
#         if capacity:
#             query += " AND r.capacity >= %s"
#             query_params.append(int(capacity))
#
#         if room_name:
#             query += " AND r.room_name LIKE %s"
#             query_params.append(f"%{room_name}%")
#
#         if date:
#             formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
#             query += " AND DATE(ra.available_date) = %s"
#             query_params.append(formatted_date)
#
#         if start_time:
#             query += " AND ra.available_begin >= %s"
#             query_params.append(f"{start_time}:00")
#
#         if end_time:
#             query += " AND ra.available_end <= %s"
#             query_params.append(f"{end_time}:00")
#
#         if equipment:
#             query += " AND r.equipment LIKE %s"
#             query_params.append(f"%{equipment}%")
#
#         # 调试输出SQL
#         print("[调试] 最终SQL:", query)
#         print("[调试] 参数:", query_params)
#
#         # 执行查询
#         cursor.execute(query, query_params)
#         results = cursor.fetchall()
#
#         # 格式化时间字段
#         for result in results:
#             result['available_begin'] = format_time(result['available_begin'])
#             result['available_end'] = format_time(result['available_end'])
#
#         return jsonify({
#             "count": len(results),
#             "results": results
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# @app.route('/bookings', methods=['GET'])
# def get_all_bookings():
#     """
#     获取所有房间预约记录的接口。
#     示例请求：
#     fetch('https://101.200.197.132:5000/bookings')
#     .then(response => response.json())
#     .then(data => console.log('Bookings:', data))
#     .catch(error => console.error('Error:', error));
#     """
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         # 查询所有booking的基本信息
#         query = """
#             SELECT
#                 b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time,b.status,
#                 r.room_name, r.location, r.capacity, r.equipment
#             FROM Bookings b
#             JOIN Rooms r ON b.room_id = r.room_id
#             ORDER BY b.booking_date, b.start_time
#         """
#
#         cursor.execute(query)
#         bookings = cursor.fetchall()
#
#         # 格式化时间字段（如果有必要的话）
#         for booking in bookings:
#             booking['start_time'] = format_time(booking['start_time'])
#             booking['end_time'] = format_time(booking['end_time'])
#             booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")
#
#         return jsonify({
#             "count": len(bookings),
#             "bookings": bookings
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# @app.route('/update-room/<int:room_id>', methods=['PUT'])
# def update_room(room_id):
#     """
#     更新指定房间的信息。
#     请求体示例：
#     // 发送 PUT 请求更新房间信息
#     const roomId = 1;  // 要更新的房间 ID
#     const url = `https://101.200.197.132:5000/update-room/${roomId}`;
#     {
#         "room_name": "New Room Name",
#         "capacity": 25,
#         "equipment": "Projector, Whiteboard",
#         "location": "Building 2, Floor 1"
#     }
#     """
#     print(f"Received PUT request to update room with ID: {room_id}")  # 调试信息
#
#     data = request.json
#     print(f"Request body: {data}")  # 打印请求体
#
#     room_name = data.get('room_name')
#     capacity = data.get('capacity')
#     equipment = data.get('equipment')
#     location = data.get('location')
#
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         # 检查房间名称是否已经存在
#         cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
#         existing_room = cursor.fetchone()
#         if existing_room:
#             print(f"Room name '{room_name}' already exists.")  # 调试信息
#             return jsonify({"error": "Room name already exists"}), 400
#
#         # 构建更新的 SQL 语句
#         update_query = """
#             UPDATE Rooms
#             SET room_name = %s, capacity = %s, equipment = %s, location = %s
#             WHERE room_id = %s
#         """
#         update_params = (room_name, capacity, equipment, location, room_id)
#
#         print(f"Executing update query: {update_query} with parameters: {update_params}")  # 调试信息
#
#         # 执行更新
#         cursor.execute(update_query, update_params)
#         conn.commit()
#
#         # 检查是否有记录被更新
#         if cursor.rowcount == 0:
#             print(f"No room found with ID {room_id}.")  # 调试信息
#             return jsonify({"error": "Room not found"}), 404
#
#         # 获取更新后的房间信息
#         cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
#         updated_room = cursor.fetchone()
#         print(f"Updated room: {updated_room}")  # 打印更新后的房间信息
#
#         return jsonify({
#             "message": "Room updated successfully",
#             "room_id": updated_room[0],
#             "room_name": updated_room[1],
#             "capacity": updated_room[2],
#             "equipment": updated_room[3],
#             "location": updated_room[4]
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")  # 调试信息
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")  # 调试信息
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
# @app.route('/rooms', methods=['GET'])
# def get_rooms():
#     """
#     获取所有房间的信息。
#     返回字段：room_id, room_name, capacity, equipment, location
#     """
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         # 查询所有房间的基本信息
#         query = """
#             SELECT room_id, room_name, capacity, equipment, location
#             FROM Rooms
#         """
#
#         cursor.execute(query)
#         rooms = cursor.fetchall()
#
#         # 格式化响应数据
#         return jsonify({
#             "count": len(rooms),
#             "rooms": rooms
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# # if __name__ == '__main__':
# #     app.run(debug=True)
# if __name__ == '__main__':
#     # 添加路由打印
#     print("\nRegistered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"→ {rule}")
#     app.run(debug=True)
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import mysql.connector
# from datetime import datetime, timedelta
#
# app = Flask(__name__)
# CORS(app)
#
# # 数据库配置
# db_config = {
#     "host": "localhost",
#     "port": 3306,
#     "user": "root",
#     "password": "root",
#     "database": "booking_system_db"
# }
#
#
# def get_db_connection():
#     return mysql.connector.connect(**db_config)
#
#
# def validate_time(time_str):
#     """验证时间格式 HH:MM"""
#     try:
#         datetime.strptime(time_str, "%H:%M")
#         return True
#     except ValueError:
#         return False
#
#
# # 将 timedelta 对象转化为 HH:MM 格式字符串
# def format_time(timedelta_obj):
#     if isinstance(timedelta_obj, timedelta):
#         total_seconds = int(timedelta_obj.total_seconds())
#         hours = total_seconds // 3600
#         minutes = (total_seconds % 3600) // 60
#         return f"{hours:02}:{minutes:02}"
#     return timedelta_obj
#
#
# @app.route('/search-rooms', methods=['POST'])
# def search_rooms():
#     """
#     请求参数示例：
#     const requestData = {
#         "capacity": 20,          // 可选，>= 值
#         "room_name": "会议室",    // 可选，模糊匹配
#         "date": "2025-03-05",    // 可选，精确匹配
#         "start_time": "08:00",   // 可选，HH:MM 格式
#         "end_time": "12:00"      // 可选，HH:MM 格式
#         "equipment": "projector" //可选
#     }
#     所有参数均为可选，可以任意组合
#     // 发送POST请求
# fetch('https://101.200.197.132:5000/search-rooms', {
#     method: 'POST',
#     headers: {
#         'Content-Type': 'application/json'  // 设置请求头为JSON
#     },
#     body: JSON.stringify(requestData)  // 将请求体转为JSON字符串
# })
# .then(response => response.json())  // 解析返回的JSON数据
# .then(data => {
#     console.log('Response:', data);  // 打印返回的数据
# })
# .catch(error => {
#     console.error('Error:', error);  // 错误处理
# });
#     """
#     # 获取参数
#     params = request.json or {}
#     capacity = params.get('capacity')
#     room_name = params.get('room_name')
#     date = params.get('date')
#     start_time = params.get('start_time')
#     end_time = params.get('end_time')
#     equipment = params.get('equipment')
#
#     # 参数验证
#     if start_time and not validate_time(start_time):
#         return jsonify({"error": "Invalid start_time format (HH:MM)"}), 400
#     if end_time and not validate_time(end_time):
#         return jsonify({"error": "Invalid end_time format (HH:MM)"}), 400
#
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True, buffered=True)  # 添加buffered=True
#
#         # 构建基础查询
#         query = """
#             SELECT
#                 r.room_id, r.room_name, r.capacity, r.equipment, r.location,
#                 ra.available_date, ra.available_begin, ra.available_end, ra.availability
#             FROM Rooms r
#             JOIN Room_availability ra ON r.room_id = ra.room_id
#             WHERE ra.availability IN (0, 2)
#         """
#         query_params = []
#
#         # 动态添加条件
#         if capacity:
#             query += " AND r.capacity >= %s"
#             query_params.append(int(capacity))
#
#         if room_name:
#             query += " AND r.room_name LIKE %s"
#             query_params.append(f"%{room_name}%")
#
#         if date:
#             formatted_date = datetime.strptime(date, "%Y-%m-%d").date()
#             query += " AND DATE(ra.available_date) = %s"
#             query_params.append(formatted_date)
#
#         if start_time:
#             query += " AND ra.available_begin >= %s"
#             query_params.append(f"{start_time}:00")
#
#         if end_time:
#             query += " AND ra.available_end <= %s"
#             query_params.append(f"{end_time}:00")
#
#         if equipment:
#             query += " AND r.equipment LIKE %s"
#             query_params.append(f"%{equipment}%")
#
#         # 调试输出SQL
#         print("[调试] 最终SQL:", query)
#         print("[调试] 参数:", query_params)
#
#         # 执行查询
#         cursor.execute(query, query_params)
#         results = cursor.fetchall()
#
#         # 格式化时间字段
#         for result in results:
#             result['available_begin'] = format_time(result['available_begin'])
#             result['available_end'] = format_time(result['available_end'])
#
#         return jsonify({
#             "count": len(results),
#             "results": results
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# @app.route('/bookings', methods=['GET'])
# def get_all_bookings():
#     """
#     获取所有房间预约记录的接口。
#     示例请求：
#     fetch('https://101.200.197.132:5000/bookings')
#     .then(response => response.json())
#     .then(data => console.log('Bookings:', data))
#     .catch(error => console.error('Error:', error));
#     """
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         # 查询所有booking的基本信息
#         query = """
#             SELECT
#                 b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time,b.status,
#                 r.room_name, r.location, r.capacity, r.equipment
#             FROM Bookings b
#             JOIN Rooms r ON b.room_id = r.room_id
#             ORDER BY b.booking_date, b.start_time
#         """
#
#         cursor.execute(query)
#         bookings = cursor.fetchall()
#
#         # 格式化时间字段（如果有必要的话）
#         for booking in bookings:
#             booking['start_time'] = format_time(booking['start_time'])
#             booking['end_time'] = format_time(booking['end_time'])
#             booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")
#
#         return jsonify({
#             "count": len(bookings),
#             "bookings": bookings
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# @app.route('/update-room/<int:room_id>', methods=['PUT'])
# def update_room(room_id):
#     """
#     更新指定房间的信息。
#     请求体示例：
#     // 发送 PUT 请求更新房间信息
#     const roomId = 1;  // 要更新的房间 ID
#     const url = `https://101.200.197.132:5000/update-room/${roomId}`;
#     {
#         "room_name": "New Room Name",
#         "capacity": 25,
#         "equipment": "Projector, Whiteboard",
#         "location": "Building 2, Floor 1"
#     }
#     """
#     print(f"Received PUT request to update room with ID: {room_id}")  # 调试信息
#
#     data = request.json
#     print(f"Request body: {data}")  # 打印请求体
#
#     room_name = data.get('room_name')
#     capacity = data.get('capacity')
#     equipment = data.get('equipment')
#     location = data.get('location')
#
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
#
#         # 检查房间名称是否已经存在
#         cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
#         existing_room = cursor.fetchone()
#         if existing_room:
#             print(f"Room name '{room_name}' already exists.")  # 调试信息
#             return jsonify({"error": "Room name already exists"}), 400
#
#         # 构建更新的 SQL 语句
#         update_query = """
#             UPDATE Rooms
#             SET room_name = %s, capacity = %s, equipment = %s, location = %s
#             WHERE room_id = %s
#         """
#         update_params = (room_name, capacity, equipment, location, room_id)
#
#         print(f"Executing update query: {update_query} with parameters: {update_params}")  # 调试信息
#
#         # 执行更新
#         cursor.execute(update_query, update_params)
#         conn.commit()
#
#         # 检查是否有记录被更新
#         if cursor.rowcount == 0:
#             print(f"No room found with ID {room_id}.")  # 调试信息
#             return jsonify({"error": "Room not found"}), 404
#
#         # 获取更新后的房间信息
#         cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
#         updated_room = cursor.fetchone()
#         print(f"Updated room: {updated_room}")  # 打印更新后的房间信息
#
#         return jsonify({
#             "message": "Room updated successfully",
#             "room_id": updated_room[0],
#             "room_name": updated_room[1],
#             "capacity": updated_room[2],
#             "equipment": updated_room[3],
#             "location": updated_room[4]
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")  # 调试信息
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")  # 调试信息
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
# @app.route('/rooms', methods=['GET'])
# def get_rooms():
#     """
#     获取所有房间的信息。
#     返回字段：room_id, room_name, capacity, equipment, location
#     """
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor(dictionary=True)
#
#         # 查询所有房间的基本信息
#         query = """
#             SELECT room_id, room_name, capacity, equipment, location
#             FROM Rooms
#         """
#
#         cursor.execute(query)
#         rooms = cursor.fetchall()
#
#         # 格式化响应数据
#         return jsonify({
#             "count": len(rooms),
#             "rooms": rooms
#         })
#
#     except mysql.connector.Error as e:
#         print(f"Database error: {str(e)}")
#         return jsonify({"error": "Database error", "details": str(e)}), 500
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'conn' in locals():
#             conn.close()
#
#
# # if __name__ == '__main__':
# #     app.run(debug=True)
# if __name__ == '__main__':
#     # 添加路由打印
#     print("\nRegistered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"→ {rule}")
#     app.run(debug=True)

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

# ============================ DELETE 相关接口 ============================

# ---------------------------- 删除 Users ----------------------------
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
            # 删除依赖数据：
            # 1. 删除该用户的通知记录
            cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
            # 2. 删除该用户预订的记录，其审批记录依赖于预订（先删除审批记录）
            # 删除审批记录中 booking_id 属于该用户的预订
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
@app.route('/delete/bookings', methods=['POST', 'OPTIONS'])
def delete_bookings():
    if request.method == 'OPTIONS':
        return '', 200  # 或返回一个空的 JSON 响应

    data = request.json
    booking_id = data.get('booking_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    booking_date = data.get('booking_date')
    # status_val = data.get('status')  # 不再用于删除条件

    # 删除依赖记录：审批记录中对应的 booking_id
    dependent_query = """
    DELETE FROM Approvals 
    WHERE booking_id = %s
    """
    dependent_params = (booking_id,)
    delete_record(dependent_query, dependent_params)

    # 直接根据 booking_id 以及其他参数删除 Bookings 中的记录，不再限制 status
    query = """
    DELETE FROM Bookings
    WHERE booking_id = %s
      AND start_time = %s
      AND end_time = %s
      AND booking_date = %s
    """
    params = (booking_id, start_time, end_time, booking_date)
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

# ============================ 其他数据库相关接口 ============================

def validate_time(time_str):
    """验证时间格式 HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

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
        "capacity": 20,
        "room_name": "会议室",
        "date": "2025-03-05",
        "start_time": "08:00",
        "end_time": "12:00",
        "equipment": "projector"
    }
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
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,
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
    """
    获取所有房间预约记录的接口。
    """
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

@app.route('/update-room/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    """
    更新指定房间的信息。
    """
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
        # 检查房间名称是否已经存在
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

@app.route('/rooms', methods=['GET'])
def get_rooms():
    """
    获取所有房间的信息。
    """
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

if __name__ == '__main__':
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"→ {rule}")
    app.run(debug=True)
