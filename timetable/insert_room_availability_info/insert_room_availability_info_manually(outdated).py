from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS  # 导入 CORS 库

# 初始化 Flask 应用
app = Flask(__name__)

# 启用 CORS（允许所有来源）
CORS(app)

# 配置 MySQL 数据库连接
app.config['MYSQL_HOST'] = 'localhost'  # MySQL 主机
app.config['MYSQL_USER'] = 'root'       # MySQL 用户名
app.config['MYSQL_PASSWORD'] = '1234'  # MySQL 密码
app.config['MYSQL_DB'] = 'booking_system_db'  # 数据库名

# 初始化 MySQL
mysql = MySQL(app)

# 路由：根据 room_name 查找 room_id
@app.route('/get_room_id', methods=['POST'])
def get_room_id():
    try:
        room_name = request.json.get('room_name')

        if not room_name:
            return jsonify({"error": "Room name is required!"}), 400

        # 查询数据库获取 room_id
        cur = mysql.connection.cursor()
        cur.execute("SELECT room_id FROM Rooms WHERE room_name = %s", [room_name])
        room = cur.fetchone()

        cur.close()

        if room:
            return jsonify({"room_id": room[0]}), 200
        else:
            return jsonify({"error": "Room not found!"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 路由：根据 room_id 和其他数据更新 Room_availability
@app.route('/add_room_availability', methods=['POST'])
def add_room_availability():
    try:
        data = request.json
        room_id = data.get('room_id')
        available_date = data.get('available_date')
        available_begin = data.get('available_begin')
        available_end = data.get('available_end')
        is_available = data.get('is_available')

        # 检查是否传入了必要的数据
        if not room_id or not available_date or not available_begin or not available_end or is_available is None:
            return jsonify({"error": "All fields (room_id, available_date, available_begin, available_end, is_available) are required!"}), 400

        # 插入 Room_availability 数据
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO Room_availability (room_id, available_date, available_begin, available_end, is_available)
            VALUES (%s, %s, %s, %s, %s)
        """, (room_id, available_date, available_begin, available_end, is_available))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Room availability added successfully!"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
