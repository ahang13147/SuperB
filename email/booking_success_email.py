# -*- coding: utf-8 -*-
"""
Author: Zibang Nie
Description: This Flask application sends reminder emails to users about their room bookings.
             It retrieves booking details from the database and sends a reminder email to the user.
             The email includes booking details such as room name, location, start time, and end time.
"""

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import mysql.connector
from datetime import datetime, timedelta

app = Flask(__name__)

# 配置Flask应用
app.secret_key = 'your_secret_key'
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',  # 你的邮件服务器
    'MAIL_PORT': 587,                         # 端口（通常为587用于TLS）
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': '2530681892@qq.com',  # 邮件发送者
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',    # 邮件密码
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')  # 默认发件人
})

mail = Mail(app)

# 数据库连接设置
db_config = {
    'host': 'localhost',  # 数据库主机
    'user': 'root',  # 数据库用户名
    'password': '1234',  # 数据库密码
    'database': 'booking_system_db'  # 数据库名称
}

def fetch_booking_info(booking_id):
    """从数据库获取用户和房间信息"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True  # 禁用 SSL
        )
        cursor = conn.cursor()

        # 查询booking表、users表和rooms表
        query = """
        SELECT b.booking_id, u.email, r.room_name, r.location, b.start_time, b.end_time
        FROM Bookings b
        JOIN Users u ON b.user_id = u.user_id
        JOIN Rooms r ON b.room_id = r.room_id
        WHERE b.booking_id = %s
        """
        cursor.execute(query, (booking_id,))
        booking_info = cursor.fetchone()

        # 关闭数据库连接
        cursor.close()
        conn.close()

        if booking_info:
            return booking_info
        else:
            print(f"未找到预定ID {booking_id} 的记录")
            return None

    except mysql.connector.Error as err:
        print(f"数据库错误: {err}")
        return None


def send_email(to_email, subject, body):
    """发送邮件的函数"""
    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        msg.html = body  # 使用HTML格式发送邮件

        # 发送邮件
        mail.send(msg)
        print(f'邮件已发送给 {to_email}')
    except Exception as e:
        print(f'发送邮件失败: {e}')


@app.route('/send_email/booking_success', methods=['POST'])
def send_booking_success():
    """根据 booking_id 发送房间预定提醒邮件"""
    # 从前端表单获取 booking_id
    booking_id = request.form.get('booking_id', type=int)

    if not booking_id:
        flash('请输入有效的预定ID。', 'error')
        return redirect(url_for('index'))

    booking_info = fetch_booking_info(booking_id)

    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # 准备邮件内容
        subject = f"提醒: 预定房间 {room_name} 已经成功！"
        body = f"""
        尊敬的{user_email}, 

        您的房间预定已经成功！以下是您的预定信息：

        预定ID: {booking_id}
        房间名称: {room_name}
        房间位置: {room_location}
        开始时间: {start_time}
        结束时间: {end_time}
        持续时间: {start_time} - {end_time}

        请及时前往房间，谢谢。

        祝您一切顺利！
        """

        # 发送邮件
        send_email(user_email, subject, body)
        flash('提醒邮件已发送！', 'success')
    else:
        flash('未找到对应的预定信息。', 'error')

    return redirect(url_for('index'))


@app.route('/')
def index():
    """渲染主页面"""
    return render_template('booking_success_email.html')


if __name__ == '__main__':
    app.run(debug=True)
