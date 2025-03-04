from flask import Flask, jsonify, request
import mysql.connector

# 创建 Flask 应用
app = Flask(__name__)

# 配置数据库连接
db_config = {
    "host": "localhost",       # 数据库主机
    "user": "root",            # 用户名
    "password": "",    # 密码
    "database": "booking_system_db"  # 数据库名
}

# 连接到 MySQL 数据库
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 读取 SQL 文件内容
def read_sql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# 查询房间并根据参数进行过滤
@app.route('/rooms', methods=['GET'])
def get_rooms():
    # 获取查询参数，默认值为 None
    capacity = request.args.get('capacity', type=int)
    equipment = request.args.get('equipment', type=str)
    available_date = request.args.get('available_date', type=str)
    available_begin = request.args.get('available_begin', type=str)
    available_end = request.args.get('available_end', type=str)

    # 打印查询参数，用于调试
    print(f"Received query parameters: capacity={capacity}, equipment={equipment}, available_date={available_date}, available_begin={available_begin}, available_end={available_end}")

    # 连接数据库
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 读取 search.sql 文件内容
    query = read_sql_file('search.sql')

    # 执行查询，使用查询参数
    cursor.execute(query, (capacity, equipment, available_date, available_begin, available_end))

    # 获取查询结果
    rooms = cursor.fetchall()

    # 关闭数据库连接
    cursor.close()
    conn.close()

    # 返回查询结果，转换为 JSON 格式
    return jsonify(rooms)

if __name__ == '__main__':
    app.run(debug=True)
