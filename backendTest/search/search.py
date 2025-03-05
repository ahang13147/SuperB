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
    "port": 3306,
    "user": "root",
    "password": "root",  # 替换为你的密码
    "database": "booking_system_db"
}


# 连接到 MySQL 数据库
def get_db_connection():
    return mysql.connector.connect(**db_config)


# 执行查询操作
def search_records(query, params):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # 使用 dictionary 返回结果，以便于 JSON 化
        cursor.execute(query, params)
        records = cursor.fetchall()  # 获取所有查询结果
        return records, 200
    except mysql.connector.Error as e:
        print(e)
        return f"Error occurred: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


# 动态构建查询 SQL
def build_search_query(table, conditions):
    query = f"SELECT * FROM {table} WHERE "
    query_conditions = []

    # 遍历所有条件字段，动态生成条件
    params = []
    for field, value in conditions.items():
        if value is not None:
            query_conditions.append(f"{field} = %s")
            params.append(value)
        # else:
        #     query_conditions.append(f"{field} IS NULL")

    query += " AND ".join(query_conditions)
    return query, params


# 定义查询 API 路由
@app.route('/search', methods=['POST'])
def search():
    # 从请求中获取表名和条件字段
    table = request.json.get('table')
    conditions = request.json.get('conditions')

    if not table or not conditions:
        return jsonify({"error": "Table and conditions are required"}), 400

    # 构建 SQL 查询
    query, params = build_search_query(table, conditions)

    # 执行查询操作
    result, status_code = search_records(query, params)
    if status_code == 200 and not result:
        return jsonify({"message": "No records found"}), 200

    return jsonify({"data": result}), status_code


if __name__ == '__main__':
    app.run(debug=True)
