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

@app.route('/add_room', methods=['POST'])
def add_room():
    try:
        # 从前端请求中获取数据
        room_name = request.json.get('room_name')
        capacity = request.json.get('capacity')
        equipment = request.json.get('equipment')
        location = request.json.get('location')

        # 检查是否传入了所有必需的字段
        if not room_name or not capacity or not equipment or not location:
            return jsonify({"error": "All fields (room_name, capacity, equipment, location) are required!"}), 400

        # 创建数据库连接
        cur = mysql.connection.cursor()

        # 向 Rooms 表插入数据
        cur.execute(""" 
            INSERT INTO Rooms (room_name, capacity, equipment, location)
            VALUES (%s, %s, %s, %s)
        """, (room_name, capacity, equipment, location))

        # 提交到数据库
        mysql.connection.commit()

        # 关闭数据库连接
        cur.close()

        return jsonify({"message": "Room added successfully!"}), 201

    except Exception as e:
        # 异常处理
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
