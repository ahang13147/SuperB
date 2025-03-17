import pymysql
import re

# 配置 MySQL 连接
host = 'localhost'  # 数据库主机地址
user = 'root'  # MySQL 用户名
password = '1234'  # MySQL 密码
database = 'booking_system_db'  # 目标数据库名，确保数据库已经存在

# 创建数据库连接
connection = pymysql.connect(host=host, user=user, password=password, database=database)
cursor = connection.cursor()


# 定义执行SQL文件的函数，移除 MySQL 特定的注释
def execute_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        sql = file.read()  # 读取SQL文件内容

        # 删除 /*!...*/ 类型的注释
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)

        # 执行 SQL 脚本
        cursor.execute(sql)


# 按顺序执行三个SQL文件
try:
    execute_sql_file('create.sql')  # 执行 create.sql
    execute_sql_file('advanced.sql')  # 执行 advanced.sql
    execute_sql_file('insert.sql')  # 执行 insert.sql
    connection.commit()  # 提交事务
    print("SQL文件已按顺序执行成功！")
except pymysql.MySQLError as e:
    print(f"数据库错误: {e}")
finally:
    # 关闭数据库连接
    cursor.close()
    connection.close()
