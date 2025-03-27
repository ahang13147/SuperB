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
    "password": "youjiawei3",
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
    const requestData = {
        "capacity": 20,          // 可选，>= 值
        "room_name": "会议室",    // 可选，模糊匹配
        "date": "2025-03-05",    // 可选，精确匹配
        "start_time": "08:00",   // 可选，HH:MM 格式
        "end_time": "12:00"      // 可选，HH:MM 格式
        "equipment": "projector" //可选
    }
    所有参数均为可选，可以任意组合
    // 发送POST请求
fetch('https://101.200.197.132:5000/search-rooms', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'  // 设置请求头为JSON
    },
    body: JSON.stringify(requestData)  // 将请求体转为JSON字符串
})
.then(response => response.json())  // 解析返回的JSON数据
.then(data => {
    console.log('Response:', data);  // 打印返回的数据
})
.catch(error => {
    console.error('Error:', error);  // 错误处理
});
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
        cursor = conn.cursor(dictionary=True, buffered=True)  # 添加buffered=True

        # 构建基础查询
        query = """
            SELECT 
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,
                ra.available_date, ra.available_begin, ra.available_end, ra.availability
            FROM Rooms r
            JOIN Room_availability ra ON r.room_id = ra.room_id
            WHERE ra.availability IN (0, 2)
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

        # 调试输出SQL
        print("[调试] 最终SQL:", query)
        print("[调试] 参数:", query_params)

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


@app.route('/bookings', methods=['GET'])
def get_all_bookings():
    """
    获取所有房间预约记录的接口。
    示例请求：
    fetch('https://101.200.197.132:5000/bookings')
    .then(response => response.json())
    .then(data => console.log('Bookings:', data))
    .catch(error => console.error('Error:', error));
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 查询所有booking的基本信息
        query = """
            SELECT 
                b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time,b.status,
                r.room_name, r.location, r.capacity, r.equipment
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            ORDER BY b.booking_date, b.start_time
        """

        cursor.execute(query)
        bookings = cursor.fetchall()

        # 格式化时间字段（如果有必要的话）
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
    请求体示例：
    // 发送 PUT 请求更新房间信息
    const roomId = 1;  // 要更新的房间 ID
    const url = `https://101.200.197.132:5000/update-room/${roomId}`; 
    {
        "room_name": "New Room Name",
        "capacity": 25,
        "equipment": "Projector, Whiteboard",
        "location": "Building 2, Floor 1"
    }
    """
    print(f"Received PUT request to update room with ID: {room_id}")  # 调试信息

    data = request.json
    print(f"Request body: {data}")  # 打印请求体

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
            print(f"Room name '{room_name}' already exists.")  # 调试信息
            return jsonify({"error": "Room name already exists"}), 400

        # 构建更新的 SQL 语句
        update_query = """
            UPDATE Rooms
            SET room_name = %s, capacity = %s, equipment = %s, location = %s
            WHERE room_id = %s
        """
        update_params = (room_name, capacity, equipment, location, room_id)

        print(f"Executing update query: {update_query} with parameters: {update_params}")  # 调试信息

        # 执行更新
        cursor.execute(update_query, update_params)
        conn.commit()

        # 检查是否有记录被更新
        if cursor.rowcount == 0:
            print(f"No room found with ID {room_id}.")  # 调试信息
            return jsonify({"error": "Room not found"}), 404

        # 获取更新后的房间信息
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        updated_room = cursor.fetchone()
        print(f"Updated room: {updated_room}")  # 打印更新后的房间信息

        return jsonify({
            "message": "Room updated successfully",
            "room_id": updated_room[0],
            "room_name": updated_room[1],
            "capacity": updated_room[2],
            "equipment": updated_room[3],
            "location": updated_room[4]
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")  # 调试信息
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # 调试信息
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
    返回字段：room_id, room_name, capacity, equipment, location
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 查询所有房间的基本信息
        query = """
            SELECT room_id, room_name, capacity, equipment, location
            FROM Rooms
        """

        cursor.execute(query)
        rooms = cursor.fetchall()

        # 格式化响应数据
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
    fetch('https://101.200.197.132:5000/insert_booking', {
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
    fetch('https://101.200.197.132:5000/insert_room', {
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

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    # 添加路由打印
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"→ {rule}")
    app.run(debug=True)
