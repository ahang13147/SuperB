from flask import Flask, request, jsonify
from flask_cors import CORS  # 引入 Flask-CORS
import mysql.connector

# 初始化 Flask 应用
app = Flask(__name__)

# 启用跨域支持
CORS(app)  # 允许所有来源访问，如果想限制特定来源，可以进行配置

# 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",  # 填入数据库密码
    "database": "booking_system_db"
}

# 连接到 MySQL 数据库
def get_db_connection():
    return mysql.connector.connect(**db_config)


# 执行删除操作
def delete_record(query, params):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        conn.commit()  # 提交事务
        return "Deletion successful.", 200
    except Exception as e:
        conn.rollback()  # 回滚事务
        return f"Error occurred: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


# 动态构建删除 SQL
def build_delete_query(table, conditions):
    query = f"DELETE FROM {table} WHERE "
    query_conditions = []
    params = []

    # 为Bookings表格的删除构建查询
    if table == "Bookings":
        # 获取 room_id
        room_name = conditions.get("room_name")
        if room_name:
            query_conditions.append("room_id = (SELECT room_id FROM Rooms WHERE room_name = %s)")
            params.append(room_name)

        # 添加时间和日期条件
        start_time = conditions.get("start_time")
        end_time = conditions.get("end_time")
        booking_date = conditions.get("booking_date")
        status = conditions.get("status")

        if start_time:
            query_conditions.append("start_time = %s")
            params.append(start_time)
        if end_time:
            query_conditions.append("end_time = %s")
            params.append(end_time)
        if booking_date:
            query_conditions.append("booking_date = %s")
            params.append(booking_date)
        if status:
            query_conditions.append("status = %s")
            params.append(status)

    else:
        # 对于其他表的删除，按照通用条件来构建
        for field, value in conditions.items():
            if value is not None:
                query_conditions.append(f"{field} = %s")
                params.append(value)
            else:
                query_conditions.append(f"{field} IS NULL")

    query += " AND ".join(query_conditions)
    return query, params


# 定义删除 API 路由
@app.route('/delete', methods=['POST'])
def delete():
    # 从请求中获取表名和条件字段
    table = request.json.get('table')
    conditions = request.json.get('conditions')

    if not table or not conditions:
        return jsonify({"error": "Table and conditions are required"}), 400

    # 构建 SQL 删除查询
    query, params = build_delete_query(table, conditions)

    # 执行删除操作
    result, status_code = delete_record(query, params)
    return jsonify({"message": result}), status_code


if __name__ == '__main__':
    app.run(debug=True)
