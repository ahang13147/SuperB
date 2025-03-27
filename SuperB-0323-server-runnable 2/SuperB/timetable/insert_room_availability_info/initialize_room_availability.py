import pymysql
from datetime import datetime, timedelta

# 配置 MySQL 连接
host = 'localhost'  # 数据库主机地址
user = 'root'  # MySQL 用户名
password = '1234'  # MySQL 密码
database = 'booking_system_db'  # 目标数据库名，确保数据库已经存在

# 创建数据库连接
connection = pymysql.connect(host=host, user=user, password=password, database=database)
cursor = connection.cursor()

# 定义房间时段（每个房间的可用时段）
availability_times = [
    ("08:00", "08:45"),
    ("08:55", "09:40"),
    ("10:00", "10:45"),
    ("10:55", "11:40"),
    ("14:00", "14:45"),
    ("14:55", "15:40"),
    ("16:00", "16:45"),
    ("16:55", "17:40"),
    ("19:00", "19:45"),
    ("19:55", "20:40")
]

# 获取所有的 room_id
cursor.execute("SELECT room_id FROM Rooms")
rooms = cursor.fetchall()

# 获取当前日期，并计算本周的所有日期（从周一到周日）
today = datetime.today()
start_of_week = today - timedelta(days=today.weekday())  # 本周一的日期
dates_this_week = [start_of_week + timedelta(days=i) for i in range(7)]  # 本周的7天

# 为每个房间插入对应的 room_availability 记录
try:
    for room in rooms:
        room_id = room[0]

        # 为当前房间的每个时段和每个日期插入记录
        for start_time, end_time in availability_times:
            for date in dates_this_week:
                cursor.execute("""
                    INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability)
                    VALUES (%s, %s, %s, %s, 0)  -- 设置每个时段的可用性为 0
                """, (room_id, start_time, end_time, date.strftime('%Y-%m-%d')))

    # 提交事务
    connection.commit()
    print("房间可用性记录已成功插入！")

except pymysql.MySQLError as e:
    print(f"数据库错误: {e}")
    connection.rollback()

finally:
    # 关闭数据库连接
    cursor.close()
    connection.close()
