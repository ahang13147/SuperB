from flask import Flask, request, jsonify
from flask_cors import CORS  # 引入 Flask-CORS 用于处理跨域
import mysql.connector

# 初始化 Flask 应用
app = Flask(__name__)

# 启用跨域支持
CORS(app, supports_credentials=True)  # 允许所有来源访问，如果想限制特定来源，可以进行配置

# 数据库连接配置
db_config = {
    "host": "localhost",
    "user": "root",
    "password": " ",  # 填入数据库密码
    "database": "booking_system_db"
}

# 连接到 MySQL 数据库
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 执行查询操作
def search_records(query, params):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # 使用 dictionary 返回结果，以便于 JSON 化

    try:
        cursor.execute(query, params)
        records = cursor.fetchall()  # 获取所有查询结果
        return records, 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()

# 动态构建查询 SQL
def build_search_query(conditions):
    query = """
    SELECT r.room_id, r.room_name, r.capacity, r.equipment, r.location, ra.available_date, ra.available_begin, ra.available_end
    FROM Rooms r
    JOIN Room_availability ra ON r.room_id = ra.room_id
    WHERE ra.is_available = 1
    """
    query_conditions = []
    params = []

    # 如果所有条件都为空，则返回所有有空时间的表
    if all(value is None for value in conditions.values()):
        query_conditions.append("ra.available_date IS NOT NULL AND ra.available_begin IS NOT NULL AND ra.available_end IS NOT NULL")
    else:
        # 动态生成查询条件
        for field, value in conditions.items():
            if value is not None:
                if field == 'equipment':
                    query_conditions.append(f"r.{field} LIKE %s")  # 设备使用 LIKE 进行模糊匹配
                    params.append(f"%{value}%")  # 模糊查询：前后加上%进行匹配
                else:
                    query_conditions.append(f"r.{field} = %s")  # 其他字段直接使用等式
                    params.append(value)
            elif field in ['available_date', 'available_begin', 'available_end']:
                # 如果日期、开始时间、结束时间为空，允许匹配所有有时间段的记录
                continue

    if query_conditions:
        query += " AND ".join(query_conditions)
    else:
        query += "1"  # If no conditions, return all rows

    return query, params


# 定义查询 API 路由
@app.route('/search', methods=['POST'])
def search():
    conditions = request.json.get('conditions')

    # 打印收到的查询条件
    print("Received search conditions:", conditions)

    if not conditions:
        return jsonify({"error": "Conditions are required"}), 400

    # 构建 SQL 查询
    query, params = build_search_query(conditions)

    # 打印构建的查询语句和参数
    print("Generated query:", query)
    print("With parameters:", params)

    # 执行查询操作
    result, status_code = search_records(query, params)

    # 打印查询结果
    print("Query result:", result)

    if status_code == 200 and not result:
        return jsonify({"message": "No records found"}), 200

    return jsonify({"data": result}), status_code


if __name__ == '__main__':
    app.run(debug=True)
