#  @version: 3/12/2025
#  @author: Xin Yu, Siyan Guo, Zibang Nie
# add: finished-workflow-booking get api
from contextlib import closing
from flask import Flask, redirect, request, session, url_for, render_template, jsonify
from flask_mail import Mail, Message
from functools import wraps
from flask_cors import CORS
import mysql.connector
import requests
import random
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import date, datetime, timedelta, timezone
import yaml
import msal
import csv
import pymysql
import urllib.parse


import itertools

from flask_session import Session
from multiprocessing import Process
from werkzeug.utils import secure_filename

app = Flask(__name__)
# 设置 session 持久化
app.config['SESSION_PERMANENT'] = True  # 启用持久会话
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)  # Set session duration to 3 hours
CORS(app, supports_credentials=True, origins=["https://www.diicsu.top:8000"])  # 允许所有来源访问
app.secret_key = 'your-secret-key-here'



# --------------------------log out-------------------------------

@app.route('/log_out', methods=['POST'])
def log_out():
    try:
        # Clear all session data
        session.clear()

        # Causes the cookie to expire immediately
        response = jsonify({
            "status": "success",
            "message": "You have logged out of the system"
        })
        response.set_cookie('session', '', expires=0)

        return response, 200

    except Exception as e:
        app.logger.error(f'Logout failure: {str(e)}')
        return jsonify({
            "status": "error",
            "message": "An error occurred while exiting"
        }), 500



# ---------------------------- import config----------------------------
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "root",  # 注意：删除操作中使用的是1234，请保持一致
#     "database": "booking_system_db"
# }
#
# def get_db_connection():
#     return mysql.connector.connect(**db_config)

# --------------------------email-config--------------------------

# app.config.update({
#     'MAIL_SERVER': 'smtp.qq.com',
#     'MAIL_PORT': 587,
#     'MAIL_USE_TLS': True,       # 使用 TLS 加密
#     'MAIL_USE_SSL': False,      # 不使用 SSL
#     'MAIL_USERNAME': '2530681892@qq.com',
#     'MAIL_PASSWORD': 'gnpunomuoqwhechd',
#     'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')
# })


email_accounts = [
    {
        'MAIL_USERNAME': '2530681892@qq.com',
        'MAIL_PASSWORD': 'gnpunomuoqwhechd',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')
    },
    {
        'MAIL_USERNAME': '3076129093@qq.com',
        'MAIL_PASSWORD': 'lbkbdfhwjskpdfcg',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '3076129093@qq.com')
    },
    {
        'MAIL_USERNAME': '3030954581@qq.com',
        'MAIL_PASSWORD': 'kpxnfzxcjjkgdhdh',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '3030954581@qq.com')
    },
    {
        'MAIL_USERNAME': '2769853497@qq.com',
        'MAIL_PASSWORD': 'rzymctqoaukldebd',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '2769853497@qq.com')
    },
    {
        'MAIL_USERNAME': '3414761872@qq.com',
        'MAIL_PASSWORD': 'ixrrunvbmcljcjie',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '3414761872@qq.com')
    },
    {
        'MAIL_USERNAME': '3063462656@qq.com',
        'MAIL_PASSWORD': 'rzmichcrkblydfhd',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '3063462656@qq.com')
    },
    {
        'MAIL_USERNAME': '2036223686@qq.com',
        'MAIL_PASSWORD': 'sxlrhyfxytugddhh',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '2036223686@qq.com')
    },
    {
        'MAIL_USERNAME': '2816274139@qq.com',
        'MAIL_PASSWORD': 'rpfhyzgydjpldggi',
        'MAIL_DEFAULT_SENDER': ('Classroom System', '2816274139@qq.com')
    },
    # Add more email accounts as needed
]

# Shuffle the email accounts list when the app starts
random.shuffle(email_accounts)

email_cycle = itertools.cycle(email_accounts)


def get_next_email_config():
    return next(email_cycle)


def update_email_config(email_config):
    app.config.update({
        'MAIL_SERVER': 'smtp.qq.com',  # Email server
        'MAIL_PORT': 587,  # Port (587 for TLS)
        'MAIL_USE_TLS': True,
        'MAIL_USERNAME': email_config['MAIL_USERNAME'],  # Sender's email
        'MAIL_PASSWORD': email_config['MAIL_PASSWORD'],  # Sender's email password
        'MAIL_DEFAULT_SENDER': email_config['MAIL_DEFAULT_SENDER']  # Default sender
    })

    # Re-initialize the mail object after config update
    global mail
    mail = Mail(app)


# -------------------------profile-photo-config----------------

app.config['UPLOAD_FOLDER'] = 'static/uploads/avatars'  # 实际存储路径
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 限制为 2MB


# -------------------------profile-photo-----------------------

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    user_id = get_user_id_by_email()  # 调用你的现有方法
    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # 生成唯一文件名
    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    # 保存文件
    file.save(save_path)

    # --- 修改用户记录关联逻辑 ---
    user = User.query.filter_by(user_id=user_id).first()  # 根据你的字段名 user_id 查询
    if not user:
        return jsonify({'error': 'User database record not found'}), 404

    # 更新头像路径（注意字段名是否叫 avatar_path）
    user.avatar_path = os.path.join('avatars', unique_name)
    db.session.commit()

    # 生成访问 URL
    avatar_url = url_for('static', filename=f"uploads/{user.avatar_path}", _external=True)

    return jsonify({'url': avatar_url})


# -------------------------profile-photo-----------------------
#
# @app.route('/upload-avatar', methods=['POST'])
# def upload_avatar():
#     user_id = get_user_id_by_email()  # 调用你的现有方法
#     if not user_id:
#         return jsonify({'error': 'User not found'}), 404
#
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'}), 400
#
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'error': 'Empty filename'}), 400
#
#     if not allowed_file(file.filename):
#         return jsonify({'error': 'File type not allowed'}), 400
#
#     # 生成唯一文件名
#     filename = secure_filename(file.filename)
#     unique_name = f"{uuid.uuid4().hex}_{filename}"
#     save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
#
#     # 保存文件
#     file.save(save_path)
#
#     # --- 修改用户记录关联逻辑 ---
#     user = User.query.filter_by(user_id=user_id).first()  # 根据你的字段名 user_id 查询
#     if not user:
#         return jsonify({'error': 'User database record not found'}), 404
#
#     # 更新头像路径（注意字段名是否叫 avatar_path）
#     user.avatar_path = os.path.join('avatars', unique_name)
#     db.session.commit()
#
#     # 生成访问 URL
#     avatar_url = url_for('static', filename=f"uploads/{user.avatar_path}", _external=True)
#
#     return jsonify({'url': avatar_url})
#
#
# # 允许的文件类型白名单
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#
#
# def allowed_file(filename):
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS





def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --------------------------email---------------------------

mail = Mail(app)
verification_codes = {}  # 用于存储各邮箱的验证码及发送时间
code_expiry = 300  # 验证码有效时间，单位为秒（5 分钟）


@app.route('/send_verification', methods=['POST'])
def send_verification():
    """
    接收 JSON 格式的请求数据，包含邮箱地址，生成并发送验证码到该邮箱。
    要求邮箱必须以 "@dundee.ac.uk" 结尾。

    请求示例（JSON）:
    {
        "email": "your_email@dundee.ac.uk"
    }

    返回示例（JSON）:
    成功:
    {
        "status": "success",
        "message": "Verification code sent. Check your email."
    }
    失败:
    {
        "status": "failed",
        "message": "错误信息..."
    }
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing email parameter'}), 400

    email = data.get('email')

    if not email.endswith('@dundee.ac.uk'):
        return jsonify({'status': 'failed', 'message': 'The email must be from the dundee.ac.uk domain'}), 400

    # 生成随机6位验证码
    verification_code = random.randint(100000, 999999)
    # 将验证码及当前时间存入字典
    verification_codes[email] = {
        'code': verification_code,
        'timestamp': time.time()
    }

    try:
        # 构造邮件消息
        msg = Message('Verification Code - Classroom System Login', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        msg.html = f'<p>Your verification code is: <strong>{verification_code}</strong></p>'
        # 发送邮件
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Verification code sent. Check your email.'})
    except Exception as e:
        return jsonify({'status': 'failed', 'message': f'Failed to send email: {str(e)}'}), 500


@app.route('/verify', methods=['POST'])
def verify():
    """
    验证验证码并处理用户跳转
    请求格式（JSON）:
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    data = request.get_json()

    # 基础参数校验
    if not data or 'email' not in data or 'code' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing required parameters'}), 400

    email = data['email'].lower().strip()  # 邮箱标准化处理
    code = data['code']

    # 验证码格式检查
    try:
        entered_code = int(code)
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'Invalid code format'}), 400

    # 验证码有效性检查
    if email not in verification_codes:
        return jsonify({'status': 'failed', 'message': 'Invalid email address'}), 400

    stored_data = verification_codes[email]
    if time.time() - stored_data['timestamp'] > code_expiry:
        del verification_codes[email]
        return jsonify({'status': 'failed', 'message': 'Verification code expired'}), 400

        # 核心验证逻辑
    if entered_code != stored_data['code']:
        return jsonify({'status': 'failed', 'message': 'Incorrect verification code'}), 400

        # 验证通过后清理验证码
    del verification_codes[email]

    # 设置会话信息
    session.permanent = True
    session['user_email'] = email

    if is_user_blacklisted():  # 假设已实现黑名单检查函数
        return jsonify({
            'status': 'success',
            'redirect': url_for('black')
        })

        # 获取用户角色
    try:
        role_api_url = f"https://www.diicsu.top:8000/login_get_role?email={email}"
        role_response = requests.get(role_api_url, verify=False, timeout=5)

        if role_response.status_code == 200:
            role_data = role_response.json()
            user_role = role_data.get('role', 'user')
            session['user_role'] = user_role
        else:
            session['user_role'] = 'student'  # 默认角色
    except Exception as e:
        app.logger.error(f"Role API error: {str(e)}")
        session['user_role'] = 'user'

        # 角色导向跳转
    if session.get('user_role') == 'admin':
        return jsonify({
            'status': 'success',
            'redirect': url_for('booking_centre_admin')
        })
    else:
        return jsonify({
            'status': 'success',
            'redirect': url_for('booking_centre')
        })


# ----------------------------status_email----------------------
@app.route('/send_email/calendar_invite', methods=['POST'])
def send_calendar_invite():
    """
    Create an Outlook calendar event link and send via email.

    Request JSON Format:
    {
        "room_id": 1,
        "booking_date": "2025-3-26",
        "start_time": "08:45:00",
        "end_time": "09:30:00"
    }

    Response JSON Format:
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    data = request.get_json()
    required_fields = ['room_id', 'booking_date', 'start_time', 'end_time']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'status': 'failed', 'message': 'Missing required fields'}), 400

    # Example email address
    user_email = session.get('user_email')

    if not user_email:
        return jsonify({'status': 'failed', 'message': 'User email not found in session.'}), 403

    room_id = data['room_id']
    booking_date = data['booking_date'].strip()
    start_time = data['start_time'].strip()  # e.g. "08:45:00"
    end_time = data['end_time'].strip()  # e.g. "09:30:00"

    room_name = get_room_name_by_id(room_id)
    print(f"[DEBUG] Room name: {room_name}")

    try:
        beijing_tz = timezone(timedelta(hours=8))
        start_dt = datetime.strptime(f"{booking_date}T{start_time}", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=beijing_tz)
        end_dt = datetime.strptime(f"{booking_date}T{end_time}", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=beijing_tz)

        start_iso = start_dt.isoformat()
        end_iso = end_dt.isoformat()
    except ValueError as e:
        return jsonify({'status': 'failed', 'message': f'Invalid date/time format: {str(e)}'}), 400

    subject_line = f"Add booking to event – Room {room_name}"
    description = f"I have booked room {room_name} from {start_iso} to {end_iso}."
    location = f"{room_name}"
    outlook_base_url = "https://outlook.office.com/calendar/0/deeplink/compose?"
    outlook_params = {
        "subject": subject_line,
        "startdt": start_iso,
        "enddt": end_iso,
        "body": description,
        "location": location
    }
    calendar_link = outlook_base_url + urllib.parse.urlencode(outlook_params)

    # HTML body with a clickable button for the event link
    body = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
        <p>Hi,</p >
        <p>Please click the button below to add the event to your Outlook Web Calendar:</p >

        <p>
        <a href=" " 
            style="display: inline-block; padding: 10px 20px; background-color: #0078D4; color: white; text-decoration: none; border-radius: 4px;"
            target="_blank">
            Add Event
        </a >
        </p >

        <p>If the button doesn't work, you can copy and paste this link into your browser:</p >
        <p>{calendar_link}</p >

        <br>
        <p>Best regards,<br>Booking System</p >
    </body>
    </html>
    """

    process = Process(target=async_send, args=(user_email, subject_line, body))
    process.start()

    return jsonify({'status': 'success', 'message': 'Calendar invite sent via email!'})


@app.route('/send_email/communicate', methods=['POST'])
def send_communication_email():
    """
    Send a communication email in a separate process to avoid blocking the frontend.

    Request Format (JSON):
    {
        "content":"I want to report issues"
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    user_email = session.get('user_email')
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'status': 'failed', 'message': 'Failed to get content'}), 400

    content = str(data.get('message'))

    subject = f"Private_message from {user_email}"
    body = f"""Message Content:<br><br>{content}<br><br>"""

    # 创建子进程并运行邮件发送函数
    process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
    process.start()

    return jsonify({'status': 'success', 'message': 'Email is being sent in the background'})


def fetch_booking_info(booking_id):
    """
    Fetch booking details from the database using booking_id.

    Args:
        booking_id (int): The booking ID for which to fetch details.

    Returns:
        tuple: A tuple containing booking details
               (booking_id, user_email, room_name, room_location, start_time, end_time).
        If no matching booking is found, returns None.
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True  # Disable SSL
        )
        cursor = conn.cursor()

        query = """
        SELECT b.booking_id, u.email, r.room_name, r.location, b.start_time, b.end_time
        FROM Bookings b
        JOIN Users u ON b.user_id = u.user_id
        JOIN Rooms r ON b.room_id = r.room_id
        WHERE b.booking_id = %s
        """
        cursor.execute(query, (booking_id,))
        booking_info = cursor.fetchone()

        cursor.close()
        conn.close()

        if booking_info:
            return booking_info
        else:
            print(f"Booking ID {booking_id} not found")
            return None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None


def fetch_issue_info(issue_id):
    """
    Fetch issue details from the database using issue_id.

    Args:
        issue_id (int): The ID of the issue to fetch.

    Returns:
        tuple: A tuple containing issue details
               (issue_id, room_name, issue, status, start_date, start_time, end_date, end_time, added_by_email).
               Returns None if no matching issue is found.
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True  # Disable SSL
        )
        cursor = conn.cursor()

        query = """
        SELECT 
            i.issue_id,
            r.room_name,
            i.issue,
            i.status,
            i.start_date,
            i.start_time,
            i.end_date,
            i.end_time,
            u.email AS added_by_email
        FROM Issues i
        JOIN Rooms r ON i.room_id = r.room_id
        JOIN Users u ON i.added_by = u.user_id
        WHERE i.issue_id = %s
        """
        cursor.execute(query, (issue_id,))
        issue_info = cursor.fetchone()

        cursor.close()
        conn.close()

        if issue_info:
            return issue_info
        else:
            print(f"Issue ID {issue_id} not found")
            return None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None


def send_email(to_email, subject, body):
    """
    Send an email to the specified recipient.

    Args:
        to_email (str): Recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    # Get the next email configuration (cycling through accounts)
    email_config = get_next_email_config()
    #
    # # Update app config with the new email account
    update_email_config(email_config)

    try:
        msg = Message(subject, recipients=[to_email])
        msg.body = body
        msg.html = body  # Use HTML format for the email

        mail.send(msg)
        print(f'Email sent to {to_email}')
    except Exception as e:
        print(f'Failed to send email: {e}')



# Move async_send function outside the route handler
def async_send(email, subject, body):
    with app.app_context():
        try:
            send_email(email, subject, body)
            print(f"[Process] Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")



# -------------------------------
# 以下各接口均从 JSON 请求中获取 booking_id，并在返回 JSON 中包含 booking_id
# -------------------------------

@app.route('/send_email/success', methods=['POST'])
def send_success_email():
    """
    Send an email notifying the user that their booking was successful.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Successful: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        Congratulations! Your room booking has been successfully confirmed. Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br><br>

        Thank you for using our system, and we hope you enjoy your booking!
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking successful email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


@app.route('/send_email/rejected', methods=['POST'])
def send_rejected_email():
    """
    Send an email notifying the user that their booking was rejected by the administrator.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Rejected: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        We regret to inform you that your room booking request has been rejected by the administrator. Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br><br>

        Please contact the administrator for further clarification.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking rejected email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



@app.route('/send_email/cancelled', methods=['POST'])
def send_cancelled_email():
    """
    Send an email notifying the user that their booking has been cancelled.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Cancelled: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        We regret to inform you that your room booking has been cancelled. Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br><br>

        Thank you for your understanding.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking cancelled email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



@app.route('/send_email/cancelled_user', methods=['POST'])
def send_cancelled_email_user():
    """
    Send an email notifying the user that their booking has been cancelled.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Cancelled: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        You have successfully canceled your booking .Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br><br>
        Thank you for using our system, and we hope you enjoy your booking!

        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking cancelled email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



@app.route('/send_email/failed', methods=['POST'])
def send_failed_email():
    """
    Send an email notifying the user that their booking failed.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Failed: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        We regret to inform you that your room booking has failed. Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br><br>

        Please check your booking details or contact the administrator for further assistance.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking failed email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


@app.route('/send_email/remind', methods=['POST'])
def send_remind_email():
    """
    Send a reminder email notifying the user that their booking is about to begin.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Reminder: Your Booking for Room {room_name} is Approaching"
        body = f"""
        Dear {user_email},<br><br>

        This is a reminder that your room booking is about to begin. Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br><br>

        Please head to the room in time. Thank you.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



def broadcast_email(subject, body):
    """
    Broadcast an email to all users in the database.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        # Establish database connection
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True  # Disable SSL
        )
        cursor = conn.cursor()

        # Query to fetch all user emails
        query = "SELECT email FROM Users"
        cursor.execute(query)
        users = cursor.fetchall()

        # Send email to each user
        for user in users:
            to_email = user[0]
            send_email(to_email, subject, body)  # Send email to the user

        cursor.close()
        conn.close()
        print(f"Broadcast email sent to {len(users)} users.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")




def async_broadcast_email(subject, body):
    """
    Async version of broadcast_email, runs in a separate process.
    """
    with app.app_context():  # 保证子进程中有 Flask 上下文（用于 send_email 等）
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                ssl_disabled=True
            )
            cursor = conn.cursor()

            query = "SELECT email FROM Users"
            cursor.execute(query)
            users = cursor.fetchall()

            for user in users:
                to_email = user[0]
                send_email(to_email, subject, body)

            cursor.close()
            conn.close()
            print(f"[Broadcast] Email sent to {len(users)} users.")

        except mysql.connector.Error as err:
            print(f"[Broadcast] Database error: {err}")
        except Exception as e:
            print(f"[Broadcast] General error: {e}")


def broadcast_email_to_all_administrators(subject, body):
    """
    Send an email to all users with the 'admin' role.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True
        )
        cursor = conn.cursor()


        # 查询所有管理员用户的邮箱
        query = "SELECT email FROM Users WHERE role = 'admin'"
        cursor.execute(query)
        admins = cursor.fetchall()

        for admin in admins:
            admin_email = admin[0]
            send_email(admin_email, subject, body)

        cursor.close()
        conn.close()
        print(f"[Admin Broadcast] Email sent to {len(admins)} administrators.")


    except mysql.connector.Error as err:
        print(f"[Admin Broadcast] Database error: {err}")
    except Exception as e:
        print(f"[Admin Broadcast] General error: {e}")



def async_broadcast_email_to_all_administrators(subject, body):
    """
    Async version of broadcast_email_to_all_administrators, runs in a separate process.

    This function will fetch all administrators from the database and send them an email.
    """
    with app.app_context():  # Ensure Flask app context is used in the subprocess
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                ssl_disabled=True
            )
            cursor = conn.cursor()

            # Query to fetch all admin emails
            query = "SELECT email FROM Users WHERE role = 'admin'"
            cursor.execute(query)
            admins = cursor.fetchall()

            for admin in admins:
                admin_email = admin[0]
                send_email(admin_email, subject, body)

            cursor.close()
            conn.close()
            print(f"[Admin Broadcast] Email sent to {len(admins)} administrators.")

        except mysql.connector.Error as err:
            print(f"[Admin Broadcast] Database error: {err}")
        except Exception as e:
            print(f"[Admin Broadcast] General error: {e}")



@app.route('/send_email/broadcast_issue', methods=['POST'])
def broadcast_issue_email():
    """
    Broadcast an issue to all users asynchronously.

    Request Format (JSON):
    {
        "issue_id": 3
    }


@app.route('/send_email/broadcast_issue', methods=['POST'])
def broadcast_issue_email():
    """
    Broadcast an issue to all users asynchronously.

    Request Format (JSON):
    {
        "issue_id": 3
    }


    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "issue_id": 3
    }
    """
    data = request.get_json()
    if not data or 'issue_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid issue ID.', 'issue_id': None}), 400

    try:
        issue_id = int(data.get('issue_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'issue_id must be an integer.', 'issue_id': None}), 400

    issue_info = fetch_issue_info(issue_id)
    if issue_info:
        issue_id, room_id, issue, status, start_date, start_time, end_date, end_time, added_by = issue_info

        subject = f"Remind: Room {room_id} has an issue"
        body = f"""
        Dear DIICSU students and staff,<br><br>

        This is a reminder that an issue is occurring in room {room_id}. Below are the issue details:<br><br>
        <strong>Room:</strong> {room_id}<br>
        <strong>Start Time:</strong> {start_date} {start_time}<br>
        <strong>End Time:</strong> {end_date if end_date else 'Not yet resolved'} {end_time if end_time else ''}<br><br>
        <strong>Issue Content:</strong> {issue}<br>
        <strong>Issue Status:</strong> {status}<br><br>

        Please avoid using the room during the affected period. Thank you.
        """

        # async process
        process = Process(target=async_broadcast_email, args=(subject, body))
        process.start()

        return jsonify(
            {'status': 'success', 'message': 'Issue broadcast is being sent in the background.', 'issue_id': issue_id})

    else:

        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


@app.route('/send_email/cancelled_user', methods=['POST'])
def send_cancelled_email_user():
    """
    Send an email notifying the user that their booking has been cancelled.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "booking_id": 123
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Cancelled: Room {room_name}"
        body = f"""
        Dear {user_email},<br><br>

        You have successfully canceled your booking .Below are your booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br><br>
        Thank you for using our system, and we hope you enjoy your booking!

        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking cancelled email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



@app.route('/send_email/broadcast_pending', methods=['POST'])
def broadcast_pending_email():
    """
    broadcast a email to notify all administrators that there is a pending booking.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Reminder: Your Booking for Room {room_name} is Approaching"

        Dear Admin,<br><br>


        This is a pending booking request waiting to be disposed. Below are booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br><br>

        Please head to the room in time. Thank you.
        """
        broadcast_email_to_all_administrators(subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!', 'booking_id': booking_id})
    else:

        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404



        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


@app.route('/send_email/broadcast_break_faith', methods=['POST'])
def broadcast_break_faith_email():
    """
    Broadcast an email to notify all administrators and related user that this user breaks faith.

    Request Format (JSON):
    {
        "user_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing user_id in JSON body'}), 400

    try:
        user_id = int(data['user_id'])
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'user_id must be an integer'}), 400

    user_info = get_user_info_by_id(user_id)
    if user_info:
        user_name, user_email = user_info

        subject = "Reminder: A user who cancels booking too many times has been added to blacklist"
        body = f"""
        A user who cancels booking too many times has been added to blacklist. Below are details:<br><br>
        <strong>User name:</strong> {user_name}<br>
        <strong>User id:</strong> {user_id}<br>
        <strong>Reason:</strong> This user has canceled bookings too many times (over 3 times) in one day.<br>
        """

        process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
        process.start()

        Please head to the room in time. Thank you.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


def broadcast_email(subject, body):
    """
    Broadcast an email to all users in the database.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        # Establish database connection
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True  # Disable SSL
        )
        cursor = conn.cursor()

        # Query to fetch all user emails
        query = "SELECT email FROM Users"
        cursor.execute(query)
        users = cursor.fetchall()

        # Send email to each user
        for user in users:
            to_email = user[0]
            send_email(to_email, subject, body)  # Send email to the user

        cursor.close()
        conn.close()
        print(f"Broadcast email sent to {len(users)} users.")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")


# todo : add send issue email and broadcast email (3.25)


def async_broadcast_email(subject, body):
    """
    Async version of broadcast_email, runs in a separate process.
    """
    with app.app_context():  # 保证子进程中有 Flask 上下文（用于 send_email 等）
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                ssl_disabled=True
            )
            cursor = conn.cursor()

            query = "SELECT email FROM Users"
            cursor.execute(query)
            users = cursor.fetchall()

            for user in users:
                to_email = user[0]
                send_email(to_email, subject, body)

            cursor.close()
            conn.close()
            print(f"[Broadcast] Email sent to {len(users)} users.")

        except mysql.connector.Error as err:
            print(f"[Broadcast] Database error: {err}")
        except Exception as e:
            print(f"[Broadcast] General error: {e}")


def broadcast_email_to_all_administrators(subject, body):
    """
    Send an email to all users with the 'admin' role.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True
        )
        cursor = conn.cursor()

        # 查询所有管理员用户的邮箱
        query = "SELECT email FROM Users WHERE role = 'admin'"
        cursor.execute(query)
        admins = cursor.fetchall()

        for admin in admins:
            admin_email = admin[0]
            send_email(admin_email, subject, body)

        cursor.close()
        conn.close()
        print(f"[Admin Broadcast] Email sent to {len(admins)} administrators.")

    except mysql.connector.Error as err:
        print(f"[Admin Broadcast] Database error: {err}")
    except Exception as e:
        print(f"[Admin Broadcast] General error: {e}")


def async_broadcast_email_to_all_administrators(subject, body):
    """
    Async version of broadcast_email_to_all_administrators, runs in a separate process.

    This function will fetch all administrators from the database and send them an email.
    """
    with app.app_context():  # Ensure Flask app context is used in the subprocess
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                ssl_disabled=True
            )
            cursor = conn.cursor()

            # Query to fetch all admin emails
            query = "SELECT email FROM Users WHERE role = 'admin'"
            cursor.execute(query)
            admins = cursor.fetchall()

            for admin in admins:
                admin_email = admin[0]
                send_email(admin_email, subject, body)

            cursor.close()
            conn.close()
            print(f"[Admin Broadcast] Email sent to {len(admins)} administrators.")

        except mysql.connector.Error as err:
            print(f"[Admin Broadcast] Database error: {err}")
        except Exception as e:
            print(f"[Admin Broadcast] General error: {e}")


@app.route('/send_email/broadcast_issue', methods=['POST'])
def broadcast_issue_email():
    """
    Broadcast an issue to all users asynchronously.

    Request Format (JSON):
    {
        "issue_id": 3
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
        "issue_id": 3
    }
    """
    data = request.get_json()
    if not data or 'issue_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid issue ID.', 'issue_id': None}), 400

    try:
        issue_id = int(data.get('issue_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'issue_id must be an integer.', 'issue_id': None}), 400

    issue_info = fetch_issue_info(issue_id)
    if issue_info:
        issue_id, room_id, issue, status, start_date, start_time, end_date, end_time, added_by = issue_info

        subject = f"Remind: Room {room_id} has an issue"
        body = f"""
        Dear DIICSU students and staff,<br><br>

        This is a reminder that an issue is occurring in room {room_id}. Below are the issue details:<br><br>
        <strong>Room:</strong> {room_id}<br>
        <strong>Start Time:</strong> {start_date} {start_time}<br>
        <strong>End Time:</strong> {end_date if end_date else 'Not yet resolved'} {end_time if end_time else ''}<br><br>
        <strong>Issue Content:</strong> {issue}<br>
        <strong>Issue Status:</strong> {status}<br><br>

        Please avoid using the room during the affected period. Thank you.
        """

        # async process
        process = Process(target=async_broadcast_email, args=(subject, body))
        process.start()

        return jsonify(
            {'status': 'success', 'message': 'Issue broadcast is being sent in the background.', 'issue_id': issue_id})
    else:
        return jsonify({'status': 'failed', 'message': 'Failed to fetch issue information.', 'issue_id': issue_id}), 404


@app.route('/send_email/broadcast_pending', methods=['POST'])
def broadcast_pending_email():
    """
    broadcast a email to notify all administrators that there is a pending booking.

    Request Format (JSON):
    {
        "booking_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    data = request.get_json()
    if not data or 'booking_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.', 'booking_id': None}), 400

    try:
        booking_id = int(data.get('booking_id'))
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'booking_id must be an integer.', 'booking_id': None}), 400

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Reminder: Your Booking for Room {room_name} is Approaching"
        body = f"""
        Dear Admin,<br><br>

        This is a pending booking request waiting to be disposed. Below are booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br><br>

        Please head to the room in time. Thank you.
        """
        broadcast_email_to_all_administrators(subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!', 'booking_id': booking_id})
    else:
        return jsonify(
            {'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


        return jsonify({'status': 'success', 'message': 'Emails have been sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No user found with the provided ID.'}), 404

@app.route('/send_email/broadcast_break_faith', methods=['POST'])
def broadcast_break_faith_email():
    """
    Broadcast an email to notify all administrators and related user that this user breaks faith.

    Request Format (JSON):
    {
        "user_id": 123
    }

    Response Format (JSON):
    {
        "status": "success" or "failed",
        "message": "...",
    }
    """
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing user_id in JSON body'}), 400

    try:
        user_id = int(data['user_id'])
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'user_id must be an integer'}), 400

    user_info = get_user_info_by_id(user_id)
    if user_info:
        user_name, user_email = user_info

        subject = "Reminder: A user who cancels booking too many times has been added to blacklist"
        body = f"""
        A user who cancels booking too many times has been added to blacklist. Below are details:<br><br>
        <strong>User name:</strong> {user_name}<br>
        <strong>User id:</strong> {user_id}<br>
        <strong>Reason:</strong> This user has canceled bookings too many times (over 3 times) in one day.<br>
        """

        process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
        process.start()

        process1 = Process(target=async_send, args=(user_email, subject, body))
        process1.start()

        return jsonify({'status': 'success', 'message': 'Emails have been sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No user found with the provided ID.'}), 404



# ------------------------------------------------------------

def load_config(config_path="config.yaml"):
    """加载配置文件并返回配置字典"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# 加载配置
config = load_config()

# 获取数据库连接配置
db_config = config.get("db_config")


def get_db_connection():
    return mysql.connector.connect(**db_config)


# 获取 Azure 配置
CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
AUTHORITY = config.get("AUTHORITY")
REDIRECT_URI = config.get("REDIRECT_URI")

# 初始化 msal 应用
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)


# ---------------------------- helper function----------------------------
def delete_record(query, params):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return "Deletion successful.", 200
    except Exception as e:
        conn.rollback()
        return f"Error occurred: {str(e)}", 500
    finally:
        cursor.close()
        conn.close()


def validate_time(time_str):
    """验证时间格式 HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def format_time(time_val):
    """
    将时间或 timedelta 对象转化为 HH:MM 格式字符串
    如果 time_val 为 datetime.time 类型，则直接转换为字符串
    """
    if isinstance(time_val, timedelta):
        total_seconds = int(time_val.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    try:
        return time_val.strftime("%H:%M")
    except Exception:
        return str(time_val)


def generate_date_range(start_date, end_date):
    """生成从 start_date 到 end_date（含）之间的所有日期列表"""
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list


def get_room_id(room_name):
    conn = get_db_connection()
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


def get_room_name_by_id(room_id):
    """
    Fetch room name by room_id from the Rooms table.

    Args:
        room_id (int): ID of the room to look up.

    Returns:
        str: The name of the room if found, or None if not found.
    """
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True
        )
        cursor = conn.cursor()

        query = "SELECT room_name FROM Rooms WHERE room_id = %s"
        cursor.execute(query, (room_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # room_name
        else:
            print(f"Room ID {room_id} not found.")
            return None

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None


def get_user_info_by_id(user_id):
    """
    Fetch user's name and email by user_id from the users table.

    Args:
        user_id (int): ID of the user to look up.

    Returns:
        tuple: (username, email) if found, or None if not found.
    """
    try:

        # 获取数据库连接
        conn = get_db_connection()
        # 手动创建 cursor（字典格式）
        cursor = conn.cursor(dictionary=True)

        try:
            # 根据 user_id 查询 username 和 email
            cursor.execute("SELECT username, email FROM Users WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
            print("debugggg blacklist:", user_info)

        finally:
            cursor.close()  # 手动关闭 cursor
        conn.close()

        if user_info:
            return user_info['username'], user_info['email']  # 使用字典方式返回 username 和 email
        else:
            print(f"User ID {user_id} not found.")
            return None  # 如果没有找到用户，返回 None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None  # 如果数据库查询出错，返回 None



# 查询用户ID
def get_user_id_by_email():
    user_email = session.get('user_email')
    if not user_email:
        return None  # 如果 session 中没有 user_email，返回 None

    try:
        # 获取数据库连接
        conn = get_db_connection()
        # 手动创建 cursor（字典格式）
        cursor = conn.cursor(dictionary=True)
        try:
            # 根据 email 查询 user_id
            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (user_email,))
            user = cursor.fetchone()
        finally:
            cursor.close()  # 手动关闭 cursor
        conn.close()

        if user:
            return user['user_id']  # 返回 user_id
        else:
            return None  # 如果没有找到对应的用户，返回 None
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None  # 如果数据库查询出错，返回 None


# ---------------------------- login ----------------------------
@app.route('/')
def index():
    # todo
    session.permanent = True  # 强制将 session 设置为持久化
    return redirect(url_for('login'))


@app.route('/auth')
def auth():
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=REDIRECT_URI,
        prompt="select_account"  # 添加此行
    )
    return redirect(auth_url)


@app.route('/auth_callback')
def auth_callback():
    # 处理Microsoft回调
    code = request.args.get('code')
    if not code:
        return "认证失败：缺少授权码", 400

    # 用授权码换取令牌
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read"],
        redirect_uri=REDIRECT_URI
    )

    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('profile'))
    else:
        return f"认证错误：{result.get('error_description')}", 500


# todo: add two new function
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('login'))  # 如果未登录，重定向到登录页面
        if is_user_blacklisted():
            return redirect(url_for('black'))
        return f(*args, **kwargs)

    return decorated_function


# 角色验证装饰器
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] != role:
                return redirect(url_for('login'))  # 如果不是指定角色，重定向到普通页面
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


# 路由：渲染 booking_centre.html
@app.route('/booking_centre')
@login_required  # 确保用户已登录
def booking_centre():
    return render_template('booking_centre.html')


@app.route('/my_reservation')
@login_required  # 确保用户已登录
def my_reservation():
    return render_template('my_reservation.html')


@app.route('/user_profile')
@login_required  # 确保用户已登录
def user_profile():
    return render_template('user_profile.html')


@app.route('/my_notification')
@login_required  # 确保用户已登录
def my_notification():
    return render_template('my_notification.html')


@app.route('/error')
def error_page():
    return render_template('error.html')  # 确保 templates/error.html 文件存在


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/adminSidebar')
@login_required  # 确保用户已登录
@role_required('admin')
def adminSidebar():
    return render_template('adminSidebar.html')


@app.route('/Approval_Center')
@login_required  # 确保用户已登录
@role_required('admin')
def Approval_Center():
    return render_template('Approval_Center.html')


@app.route('/blacklist')
@login_required  # 确保用户已登录
@role_required('admin')
def blacklist():
    return render_template('blacklist.html')


@app.route('/booking_centre_admin')
@login_required  # 确保用户已登录
@role_required('admin')
def booking_centre_admin():
    return render_template('booking_centre_admin.html')


@app.route('/cancel_reservation')
@login_required  # 确保用户已登录
@role_required('admin')
def cancel_reservation():
    return render_template('cancel_reservation.html')


@app.route('/my_profile_admin')
@login_required  # 确保用户已登录
@role_required('admin')
def my_profile_admin():
    return render_template('my_profile_admin.html')


@app.route('/my_reservation_admin')
@login_required  # 确保用户已登录
@role_required('admin')
def my_reservation_admin():
    return render_template('my_reservation_admin.html')


@app.route('/notice_admin')
@login_required  # 确保用户已登录
@role_required('admin')
def notice_admin():
    return render_template('notice_admin.html')


@app.route('/room_management')
@login_required  # 确保用户已登录
@role_required('admin')
def room_management():
    return render_template('room_management.html')


@app.route('/user_management')
@login_required  # 确保用户已登录
@role_required('admin')
def user_management():
    return render_template('user_management.html')


@app.route('/usage_report_center.html')
@login_required  # 确保用户已登录
@role_required('admin')
def usage_report_center():
    return render_template('usage_report_center.html')


@app.route('/trust_list')
@login_required  # 确保用户已登录
@role_required('admin')
def trust_list():
    return render_template('trust_list.html')


@app.route('/room_issue_management')
@login_required  # 确保用户已登录
@role_required('admin')
def room_issue_management():
    return render_template('room_issue_management.html')


@app.route('/black')
# @login_required
def black():
    return render_template('black.html')


# 路由：渲染 login.html
@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login_via_code')
def login_via_code():
    return render_template('login_via_code.html')



@app.route('/sign_off')
def sign_off():
    return render_template('sign_off.html')


# todo : add for check if the user is in blacklist
def is_user_blacklisted():
    """检查用户邮箱是否在 blacklist 表中"""
    conn = get_db_connection()
    user_id = get_user_id_by_email()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM Blacklist WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        print('blacklist debug', result)
        return result is not None
    except Exception as e:
        print(f"Error checking blacklist: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()


# TODO: 原函数
# profile route
@app.route('/profile')
def profile():
    if 'access_token' not in session:
        print("No access token in session, redirecting to login")
        return redirect(url_for('login'))

    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    try:
        print("Calling Microsoft Graph API...")
        user_info = requests.get(
            'https://graph.microsoft.com/v1.0/me?$select=mail,userPrincipalName',
            headers=headers
        ).json()
        print(f"Microsoft Graph API response: {user_info}")
    except requests.exceptions.RequestException as e:
        print(f"Microsoft API error: {str(e)}")
        return redirect(url_for('error_page'))

    # get email

    user_email = user_info.get('mail') or user_info.get('userPrincipalName')
    if not user_email:
        print("No email or userPrincipalName in Microsoft response")
        return redirect(url_for('error_page'))

    session['user_email'] = user_email
    print('debugggg', get_user_id_by_email())
    if is_user_blacklisted():
        return redirect(url_for('black'))

    # 新增：检查是否在黑名单中

    try:
        print(f"Calling role API with email: {user_email}")
        role_response = requests.get(
            f"https://www.diicsu.top:8000/login_get_role?email={user_email}",
            verify=False  # 忽略证书验证
        )
        print(f"Role API response status: {role_response.status_code}, body: {role_response.text}")

        if role_response.status_code == 200:
            role_data = role_response.json()
            user_role = role_data.get('role', 'user')
            session['user_role'] = user_role

            # redirect the URL by the role of the user

            if user_role == 'admin':
                print("User is admin, redirecting to booking_centre_admin")
                return redirect(url_for('booking_centre_admin'))
            else:
                print("User is not admin, redirecting to booking_centre")
                return redirect(url_for('booking_centre'))
        else:
            print(f"Role API call failed with status code: {role_response.status_code}")
            return redirect(url_for('error_page'))
    except Exception as e:
        print(f"Error obtaining user role: {str(e)}")
        return redirect(url_for('error_page'))


@app.route('/login_get_role', methods=['GET'])
def login_get_role():
    email = request.args.get('email')

    if not email:
        return jsonify({"error": "Missing email parameter"}), 400

    try:
        conn = get_db_connection()  # 获取数据库连接
        cursor = conn.cursor(dictionary=True)  # 创建游标

        # 执行查询
        cursor.execute("SELECT role FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()

        # 关闭游标和连接
        cursor.close()
        conn.close()

        if user:
            return jsonify({'role': user['role']})
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------- delete ----------------------------
# @app.route('/delete/users', methods=['POST'])
# def delete_users():
#     data = request.json
#     user_id = data.get('user_id')
#     username = data.get('username')
#     email = data.get('email')
#     role = data.get('role')
#     # 使用同一数据库连接和事务，先删除依赖于该用户的记录，再删除用户记录
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         if user_id:
#             # 1. 删除该用户的通知记录
#             cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
#             # 2. 删除该用户预订的记录，其审批记录依赖于预订（先删除审批记录）
#             cursor.execute("""
#                 DELETE FROM Approvals
#                 WHERE booking_id IN (
#                     SELECT booking_id FROM Bookings WHERE user_id = %s
#                 )
#             """, (user_id,))
#             # 删除该用户的预订记录
#             cursor.execute("DELETE FROM Bookings WHERE user_id = %s", (user_id,))
#             # 3. 删除审批记录中，该用户作为管理员审批的记录
#             cursor.execute("DELETE FROM Approvals WHERE admin_id = %s", (user_id,))
#             # 4. 删除该用户生成的报告
#             cursor.execute("DELETE FROM Reports WHERE admin_id = %s", (user_id,))
#         # 删除用户记录
#         query = """
#         DELETE FROM Users
#         WHERE (user_id = %s OR %s IS NULL)
#           AND (username = %s OR %s IS NULL)
#           AND (email = %s OR %s IS NULL)
#           AND (role = %s OR %s IS NULL)
#         """
#         params = (user_id, user_id, username, username, email, email, role, role)
#         cursor.execute(query, params)
#         conn.commit()
#         result = "Deletion successful."
#         status_code = 200
#     except Exception as e:
#         conn.rollback()
#         result = f"Error occurred: {str(e)}"
#         status_code = 500
#     finally:
#         cursor.close()
#         conn.close()
#     return jsonify({"message": result}), status_code


@app.route('/delete/users', methods=['POST'])
def delete_users():
    data = request.json
    user_id = data.get('user_id')

    # 使用同一数据库连接和事务，直接删除用户记录，级联删除相关数据
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if user_id:
            # 直接删除用户记录，所有相关数据将被自动删除（通过 ON DELETE CASCADE）
            cursor.execute("DELETE FROM Users WHERE user_id = %s", (user_id,))

        conn.commit()
        result = "Deletion successful."
        status_code = 200
    except Exception as e:
        conn.rollback()
        result = f"Error occurred: {str(e)}"
        status_code = 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"message": result}), status_code

@app.route('/update_room_status', methods=['POST'])
@login_required
@role_required('admin')
def update_room_status():
    data = request.get_json()
    if not data:
        return jsonify({'error': '没有收到任何 JSON 数据'}), 400

    room_id = data.get('room_id')
    action = data.get('action')

    if not room_id or not action:
        return jsonify({'error': '缺少必要的参数'}), 400

    if action not in ['delete', 'restore']:
        return jsonify({'error': '无效的操作类型'}), 400

    new_status = 2 if action == 'delete' else 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = "UPDATE Rooms SET room_status = %s WHERE room_id = %s"
        cursor.execute(update_query, (new_status, room_id))
        conn.commit()
        return jsonify({
            'message': '房间状态更新成功',
            'room_id': room_id,
            'new_status': new_status
        })
    except Exception as e:
        return jsonify({'error': '更新房间状态失败', 'details': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/delete_trusted_user', methods=['DELETE'])
def delete_trusted_user():
    data = request.get_json()
    room_id = data['room_id']
    user_id = data['user_id']

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        # 检查记录是否存在
        check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(check_query, (room_id, user_id))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"status": "error", "error": "Trusted user record not found"}), 404

        # 删除记录
        delete_query = "DELETE FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(delete_query, (room_id, user_id))
        conn.commit()
        return jsonify({"status": "success", "message": "Trusted user removed successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


@app.route('/delete_blacklist', methods=['DELETE'])
def delete_blacklist():
    data = request.get_json()
    blacklist_id = data.get('blacklist_id')
    if not blacklist_id:
        return jsonify({"status": "error", "error": "Blacklist ID is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        # 检查记录是否存在
        check_query = "SELECT * FROM Blacklist WHERE blacklist_id = %s"
        cursor.execute(check_query, (blacklist_id,))
        record = cursor.fetchone()
        if not record:
            return jsonify({"status": "error", "error": "Blacklist record not found"}), 404

        # 删除记录
        delete_query = "DELETE FROM Blacklist WHERE blacklist_id = %s"
        cursor.execute(delete_query, (blacklist_id,))
        conn.commit()
        return jsonify({"status": "success", "message": "Blacklist entry removed successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# todo : added new funtion0319
@app.route('/delete_notification', methods=['POST'])
def delete_notification():
    data = request.get_json()
    if not data or 'notification_id' not in data:
        return jsonify({"error": "Missing notification_id parameter"}), 400

    notification_id = data['notification_id']

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "DELETE FROM Notifications WHERE notification_id = %s"
        cursor.execute(query, (notification_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Notification record not found"}), 404

        return jsonify({
            "message": "Notification deleted successfully",
            "notification_id": notification_id
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to delete notification", "details": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# ---------------------------- search/display ----------------------------


@app.route('/search-rooms', methods=['POST'])
def search_rooms():
    """
    请求参数示例：
    {
        "capacity": 20,
        "room_name": "会议室",
        "date": "2025-03-05",
        "start_time": "08:00",
        "end_time": "12:00",
        "equipment": "projector"
    }
    所有参数均为可选，可以任意组合
    """
    params = request.json or {}
    capacity = params.get('capacity')
    room_name = params.get('room_name')
    date = params.get('date')
    start_time = params.get('start_time')
    end_time = params.get('end_time')
    equipment = params.get('equipment')

    if start_time and not validate_time(start_time):
        return jsonify({"error": "Invalid start_time format (HH:MM)"}), 400
    if end_time and not validate_time(end_time):
        return jsonify({"error": "Invalid end_time format (HH:MM)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = """
            SELECT 
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,r.room_type,r.room_status,
                ra.available_date, ra.available_begin, ra.available_end, ra.availability
            FROM Rooms r
            JOIN Room_availability ra ON r.room_id = ra.room_id
            WHERE ra.availability IN (0, 2)
        """
        query_params = []
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

        print("[调试] 最终SQL:", query)
        print("[调试] 参数:", query_params)

        cursor.execute(query, query_params)
        results = cursor.fetchall()

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
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
           SELECT 
    b.booking_id, 
    b.user_id, 
    u.username,  -- todo: add username field
    b.room_id, 
    b.booking_date, 
    b.start_time, 
    b.end_time, 
    b.status, 
    b.reason,
    r.room_name, 
    r.location, 
    r.capacity, 
    r.equipment
FROM Bookings b
JOIN Rooms r ON b.room_id = r.room_id
JOIN Users u ON b.user_id = u.user_id  -- JOIN Users 表，获取 username 和 user_id


        """
        cursor.execute(query)
        bookings = cursor.fetchall()
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


@app.route('/user-bookings', methods=['GET'])
def get_user_bookings():
    try:
        # 从查询参数中获取user_id
        # user_id = request.args.get('user_id')
        # todo: 添加获取当前userid
        user_id = get_user_id_by_email()
        print(user_id)
        print(session.get('user_email'))

        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                b.booking_id, 
                b.user_id, 
                u.username,  -- 添加了 username 字段
                b.room_id, 
                b.booking_date, 
                b.start_time, 
                b.end_time, 
                b.status, 
                b.reason,
                r.room_name, 
                r.location, 
                r.capacity, 
                r.equipment
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            JOIN Users u ON b.user_id = u.user_id  -- 添加了 JOIN 语句，连接 Users 表
            WHERE b.user_id = %s
            ORDER BY b.booking_date, b.start_time
        """

        cursor.execute(query, (user_id,))
        bookings = cursor.fetchall()
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


@app.route('/rooms', methods=['GET'])
def get_rooms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT room_id, room_name, capacity, equipment, location,room_type, room_status
            FROM Rooms
        """
        cursor.execute(query)
        rooms = cursor.fetchall()
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


@app.route('/pending-bookings', methods=['GET'])
def get_pending_bookings():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # todo : add user_id field
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,b.status,u.user_id,
                u.username AS user_name, r.room_name
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.status = 'pending'
            ORDER BY b.booking_date, b.start_time
        """

        # 执行查询
        cursor.execute(query)
        bookings = cursor.fetchall()

        # 格式化返回的数据
        for booking in bookings:
            booking['start_time'] = format_time(booking['start_time'])
            booking['end_time'] = format_time(booking['end_time'])
            booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")

        # 返回数据
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


@app.route('/finished-workflow-bookings', methods=['GET'])
def get_Finished_Workflow_bookings():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # todo : add user_id field
        # SQL 查询，获取状态为 'pending' 的预定记录，并连接 Users 和 Rooms 表
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,b.status,u.user_id,
                u.username AS user_name, r.room_name
            FROM Bookings b
            JOIN Users u ON b.user_id = u.user_id
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.status IN ('approved', 'rejected','failed')
            ORDER BY b.booking_date, b.start_time
        """

        # 执行查询
        cursor.execute(query)
        bookings = cursor.fetchall()

        # 格式化返回的数据
        for booking in bookings:
            booking['start_time'] = format_time(booking['start_time'])
            booking['end_time'] = format_time(booking['end_time'])
            booking['booking_date'] = booking['booking_date'].strftime("%Y-%m-%d")

        # 返回数据
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


@app.route('/get-issues/<int:room_id>', methods=['GET'])
def get_issues_by_room(room_id):
    """
    通过 room_id 获取关联的 issue 记录（仅返回 issue 和 status）
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 查询指定字段
        query = """
            SELECT 
                issue,      -- 问题描述
                status      -- 状态（fault/in_maintenance/resolved/severe）
            FROM Issues
            WHERE room_id = %s
        """
        cursor.execute(query, (room_id,))
        issues = cursor.fetchall()

        return jsonify({
            "room_id": room_id,
            "count": len(issues),
            "issues": issues  # 每个元素仅含 issue 和 status
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


@app.route('/get-blacklist-reason', methods=['GET'])
def get_blacklist_reason():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_id = get_user_id_by_email()

        # SQL 查询，连接 Blacklist 与 Users 表，获取黑名单记录和对应的 username
        query = """
          SELECT 
                u.username,
                b.start_date,
                b.start_time,
                b.end_date,
                b.end_time,
                b.reason
            FROM Blacklist b
            JOIN Users u ON b.user_id = u.user_id
            WHERE b.user_id = %s
        """

        # 执行查询
        cursor.execute(query, (user_id,))
        blacklists = cursor.fetchall()

        # 格式化日期和时间字段
        for record in blacklists:
            record['start_date'] = record['start_date'].strftime("%Y-%m-%d")
            record['start_time'] = format_time(record['start_time'])
            record['end_date'] = record['end_date'].strftime("%Y-%m-%d")
            record['end_time'] = format_time(record['end_time'])

        # 返回 JSON 格式数据
        return jsonify({
            "count": len(blacklists),
            "blacklists": blacklists
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


@app.route('/get-blacklist', methods=['GET'])
def get_blacklist():
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL 查询，连接 Blacklist 与 Users 表，获取黑名单记录和对应的 username
        query = """
            SELECT 
                b.blacklist_id,
                b.user_id,
                u.username,
                b.added_by,
                b.added_date,
                b.added_time,
                b.start_date,
                b.start_time,
                b.end_date,
                b.end_time,
                b.reason
            FROM Blacklist b
            JOIN Users u ON b.user_id = u.user_id
            ORDER BY b.added_date DESC, b.added_time DESC
        """

        # 执行查询
        cursor.execute(query)
        blacklists = cursor.fetchall()

        # 格式化日期和时间字段
        for record in blacklists:
            if record['added_date']:
                record['added_date'] = record['added_date'].strftime("%Y-%m-%d")
            if record['added_time']:
                record['added_time'] = format_time(record['added_time'])
            record['start_date'] = record['start_date'].strftime("%Y-%m-%d")
            record['start_time'] = format_time(record['start_time'])
            record['end_date'] = record['end_date'].strftime("%Y-%m-%d")
            record['end_time'] = format_time(record['end_time'])

        # 返回 JSON 格式数据
        return jsonify({
            "count": len(blacklists),
            "blacklists": blacklists
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


@app.route('/get_room_trusted_users', methods=['GET'])
def get_room_trusted_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        # 使用 dictionary=True 返回字典格式的结果
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT u.username, u.user_id, r.room_id, r.room_name
            FROM RoomTrustedUsers rt
            JOIN Users u ON rt.user_id = u.user_id
            JOIN Rooms r ON rt.room_id = r.room_id;
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return jsonify({"status": "success", "data": results})
    except mysql.connector.Error as err:
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# todo : change the method from post to GET
@app.route('/get_user', methods=['GET'])
def get_user():
    # data = request.get_json()
    # if not data or 'user_id' not in data:
    #     return jsonify({"status": "error", "error": "Missing user_id parameter"}), 400

    # todo : change user id (from current session)
    user_id = get_user_id_by_email()

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT user_id, username, email, phone_number, role FROM Users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "error": "User not found"}), 404
        return jsonify({"status": "success", "data": user})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


from datetime import timedelta


@app.route('/display-issues', methods=['GET'])
def get_all_issues():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)  # 使用字典游标

        # 获取查询参数
        status = request.args.get('status')
        room_id = request.args.get('room_id')

        # 构建查询条件和参数
        conditions = []
        params = []

        if status:
            conditions.append("i.status = %s")
            params.append(status)

        if room_id:
            # 验证room_id是否为有效整数
            if not room_id.isdigit():
                return jsonify({"error": "room_id must be a valid integer"}), 400
            conditions.append("i.room_id = %s")
            params.append(int(room_id))

        # 构建基础SQL查询
        base_query = """
            SELECT 
                i.issue_id,
                i.room_id,
                r.room_name,
                i.issue,
                i.status,
                i.start_date,
                i.start_time,
                i.end_date,
                i.end_time,
                i.added_by,
                u.username AS reporter_name
            FROM Issues i
            LEFT JOIN Rooms r ON i.room_id = r.room_id
            LEFT JOIN Users u ON i.added_by = u.user_id
        """

        # 添加WHERE条件
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        # 添加排序
        base_query += " ORDER BY i.start_date DESC"

        # 执行查询
        cursor.execute(base_query, tuple(params))
        issues = cursor.fetchall()

        # 统一格式化时间字段
        for issue in issues:
            # 处理日期
            for date_field in ['start_date', 'end_date']:
                if issue[date_field]:
                    issue[date_field] = issue[date_field].strftime("%Y-%m-%d")

            # 处理时间
            for time_field in ['start_time', 'end_time']:
                time_value = issue[time_field]
                if time_value:
                    if isinstance(time_value, timedelta):  # 处理timedelta类型
                        # 将timedelta转换为时间字符串 (HH:MM:SS)
                        total_seconds = int(time_value.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        issue[time_field] = f"{hours:02}:{minutes:02}:{seconds:02}"
                    elif isinstance(time_value, str):  # 如果已经是字符串
                        issue[time_field] = time_value
                    else:  # 处理datetime.time类型
                        issue[time_field] = time_value.strftime("%H:%M:%S")
                else:
                    issue[time_field] = None

        return jsonify({
            "count": len(issues),
            "issues": issues
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


# todo: add new function(03180117)
@app.route('/notifications', methods=['GET'])
def get_notifications():
    try:
        # 1. 通过 session 获取当前用户的 user_id
        user_id = get_user_id_by_email()
        print(user_id)
        if not user_id:
            return jsonify({"error": "Not logged in or user not found"}), 401

        # 2. 查询该用户的通知
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                notification_id,
                user_id,
                message,
                notification_action,
                created_at,
                status
            FROM Notifications
            WHERE user_id = %s OR user_id IS NULL
            ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        notifications = cursor.fetchall()

        # 3. 返回该用户的通知列表
        return jsonify({
            "count": len(notifications),
            "notifications": notifications
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


@app.route('/get_all_users_admin', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT user_id, username, email, phone_number, role FROM Users")
        users = cursor.fetchall()

        return jsonify({
            "count": len(users),
            "users": users
        }), 200

    except mysql.connector.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/top-booked-rooms', methods=['POST'])
def get_top_booked_rooms():
    """
    获取指定时间范围内总有效使用时间前5的房间
    请求参数示例：
    {
        "start_date": "2025-03-01",
        "end_date": "2025-03-31"
    }
    """
    params = request.json or {}
    start_date = params.get('start_date')
    end_date = params.get('end_date')

    # 参数验证
    if not start_date or not end_date:
        return jsonify({"error": "Missing start_date or end_date parameter"}), 400

    try:
        # 验证日期格式
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format (YYYY-MM-DD required)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 修正后的SQL（注意括号闭合）
        query = """
            SELECT 
                r.room_id,
                r.room_name,
                r.room_type,
                SUM(
                    TIMESTAMPDIFF(
                        SECOND, 
                        CONCAT(b.booking_date, ' ', b.start_time),
                        CONCAT(b.booking_date, ' ', b.end_time)
                    )
                ) AS total_seconds
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            WHERE b.status = 'finished'
                AND b.booking_date BETWEEN %s AND %s
            GROUP BY r.room_id
            ORDER BY total_seconds DESC
            LIMIT 5
        """

        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()

        # 处理结果（转换为可序列化格式）
        for room in results:
            total_seconds = room['total_seconds'] or 0
            # 计算小时数
            room['total_hours'] = round(total_seconds / 3600, 2)
            # 转换时间格式
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            room['total_duration'] = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            del room['total_seconds']  # 移除中间字段

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


# ---------------------------- update ----------------------------
@app.route('/update_user_admin', methods=['PUT'])
def update_user_admin():
    data = request.get_json() or {}
    user_id = data.get('user_id')

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    if 'email' in data:
        return jsonify({"error": "Email cannot be modified"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch existing record
        cursor.execute(
            "SELECT username, phone_number, role FROM Users WHERE user_id = %s",
            (user_id,)
        )
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"error": "User not found"}), 404

        # Determine which fields actually changed
        updates = {}
        for field in ('username', 'phone_number', 'role'):
            if field in data and data[field] != existing[field]:
                updates[field] = data[field]

        if not updates:
            return jsonify({"message": "No changes detected"}), 200

        # Build dynamic UPDATE
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        params = list(updates.values()) + [user_id]
        cursor.execute(
            f"UPDATE Users SET {set_clause} WHERE user_id = %s",
            tuple(params)
        )
        conn.commit()

        return jsonify({
            "message": "User updated successfully",
            "user_id": user_id,
            **updates
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to update user", "details": str(e)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/update-room/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    print(f"Received PUT request to update room with ID: {room_id}")
    data = request.json
    print(f"Request body: {data}")
    room_name = data.get('room_name')
    capacity = data.get('capacity')
    equipment = data.get('equipment')
    location = data.get('location')
    room_type = data.get('type')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 根据 room_id 查询当前房间数据
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        existing_room = cursor.fetchone()
        if not existing_room:
            print(f"No room found with ID {room_id}.")
            return jsonify({"error": "Room not found"}), 404

        # 检查提交数据是否与现有数据完全一致
        if (room_name == existing_room[1] and
                capacity == existing_room[2] and
                equipment == existing_room[3] and
                location == existing_room[4] and
                room_type == existing_room[5]):
            print("No changes detected.")
            return jsonify({"message": "No changes were made"}), 200

        # 检查其它记录中是否已经存在相同的房间名称（排除当前记录）
        cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
        duplicate_room = cursor.fetchone()
        if duplicate_room:
            print(f"Room name '{room_name}' already exists.")
            return jsonify({"error": "Room name already exists"}), 400

        # 执行更新操作
        update_query = """
            UPDATE Rooms
            SET room_name = %s, capacity = %s, equipment = %s, location = %s, room_type = %s
            WHERE room_id = %s
        """
        update_params = (room_name, capacity, equipment, location, room_type, room_id)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()

        if cursor.rowcount == 0:
            print(f"No changes were made during update for room id {room_id}.")
            return jsonify({"message": "No changes were made"}), 200

        # 查询并返回更新后的房间数据
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        updated_room = cursor.fetchone()
        print(f"Updated room: {updated_room}")
        return jsonify({
            "message": "Room updated successfully",
            "room_id": updated_room[0],
            "room_name": updated_room[1],
            "capacity": updated_room[2],
            "equipment": updated_room[3],
            "location": updated_room[4],
            "room_type": updated_room[5]
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


@app.route('/update-booking-status/<int:booking_id>', methods=['PUT'])
def update_booking_status(booking_id):
    print(f"Received PUT request to update booking with ID: {booking_id}")
    data = request.json
    print(f"Request body: {data}")
    status = data.get('status')

    if status not in ['approved', 'rejected']:
        return jsonify({"error": "Invalid status value. Allowed values are 'approved' or 'rejected'."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 检查该预定是否存在且状态为 pending
        cursor.execute(
            "SELECT * FROM Bookings WHERE booking_id = %s AND status = 'pending'",
            (booking_id,)
        )
        booking = cursor.fetchone()

        if not booking:
            print(f"No pending booking found with ID {booking_id}.")
            return jsonify({"error": "Booking not found or already processed"}), 404

        # 开始事务
        # 如果审批状态为 approved，需要额外更新其他冲突记录和房间状态
        if status == 'approved':
            # 1. 将当前预定更新为 approved
            cursor.execute(
                "UPDATE Bookings SET status = 'approved' WHERE booking_id = %s",
                (booking_id,)
            )

            # 2. 获取当前预定详情（用于后续更新其它记录）
            cursor.execute(
                """
                SELECT room_id, booking_date, start_time, end_time 
                FROM Bookings 
                WHERE booking_id = %s
                """,
                (booking_id,)
            )
            booking_details = cursor.fetchone()
            room_id = booking_details['room_id']
            booking_date = booking_details['booking_date']
            start_time = booking_details['start_time']
            end_time = booking_details['end_time']

            # 3. 将同一房间、同一时段中其他 pending 的记录更新为 failed
            cursor.execute(
                """
                UPDATE Bookings
                SET status = 'failed'
                WHERE room_id = %s
                  AND booking_date = %s
                  AND start_time = %s
                  AND end_time = %s
                  AND status = 'pending'
                """,
                (room_id, booking_date, start_time, end_time)
            )

            # todo
            # 查询那些被更新为 failed 的预订的 booking_id（排除掉当前审批的那个 booking）
            cursor.execute(
                """
                SELECT booking_id FROM Bookings
                WHERE room_id = %s
                  AND booking_date = %s
                  AND start_time = %s
                  AND end_time = %s
                  AND status = 'failed'
                  AND booking_id <> %s
                """,
                (room_id, booking_date, start_time, end_time, booking_id)
            )
            failed_rows = cursor.fetchall()


            # 确保 failed_booking_ids 被正确初始化
            failed_booking_ids = [row['booking_id'] for row in failed_rows] if failed_rows else []


            # 4. 更新 Room_availability 表，将对应记录的 availability 设为 2（已预订）
            cursor.execute(
                """
                UPDATE Room_availability 
                SET availability = 2 
                WHERE room_id = %s 
                  AND available_date = %s 
                  AND available_begin = %s 
                  AND available_end = %s
                """,
                (room_id, booking_date, start_time, end_time)
            )
        else:
            # 如果状态为 rejected，仅更新当前预定记录
            cursor.execute(
                "UPDATE Bookings SET status = 'rejected' WHERE booking_id = %s",
                (booking_id,)
            )
            # 不需要与 failed_bookings 相关的逻辑
            failed_booking_ids = []  # 初始化为空列表，因为 rejected 状态下不涉及失败

        # 提交事务
        conn.commit()

        # 查询更新后的预定信息
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        return jsonify({
            "message": f"Booking status updated to {updated_booking['status']}",
            "booking_id": updated_booking['booking_id'],
            "status": updated_booking['status'],
            "failed_bookings": failed_booking_ids
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        conn.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/cancel-booking/<int:booking_id>', methods=['PUT'])
def cancel_booking(booking_id):
    print(f"Received PUT request to cancel booking with ID: {booking_id}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # 获取当前登录用户 ID
        current_user_id = get_user_id_by_email()

        # 获取当前登录用户的角色
        cursor.execute("SELECT role FROM Users WHERE user_id = %s", (current_user_id,))
        role_row = cursor.fetchone()
        current_user_role = role_row['role'] if role_row else None
        print(f"Current user_id = {current_user_id}, role = {current_user_role}")


        # 查找待取消的预定记录（且尚未被取消）
        cursor.execute("""
            SELECT booking_id, user_id, booking_date, status
            FROM Bookings
            WHERE booking_id = %s
              AND status != 'canceled'
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            print(f"No booking found with ID {booking_id} or it is already canceled.")
            return jsonify({"error": "Booking not found or already canceled"}), 404

        # 如果当前用户不是管理员，则只能取消自己的 Booking
        if current_user_role != 'admin':
            if booking['user_id'] != current_user_id:
                return jsonify({"error": "You are not allowed to cancel someone else's booking"}), 403

        # 更新该预定的 status 为 'canceled'
        update_query = """
            UPDATE Bookings
            SET status = 'canceled'
            WHERE booking_id = %s
        """
        print(f"Executing update query: {update_query} with parameters: {(booking_id,)}")
        cursor.execute(update_query, (booking_id,))
        conn.commit()

        if cursor.rowcount == 0:
            print(f"Failed to cancel booking with ID {booking_id}.")
            return jsonify({"error": "Failed to cancel booking"}), 500

        # 重新获取更新后的预定信息
        cursor.execute("""
            SELECT booking_id, user_id, booking_date, status
            FROM Bookings
            WHERE booking_id = %s
        """, (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        # 如果当前用户是管理员，则不触发“取消 3 次”的逻辑，直接返回成功
        if current_user_role == 'admin':
            return jsonify({
                "message": "Booking canceled by admin",
                "booking_id": updated_booking['booking_id'],
                "status": updated_booking['status']
            })

        # 走到这里说明是普通用户自己在取消预定
        user_id = updated_booking['user_id']
        booking_date = updated_booking['booking_date']

        # 统计该用户在同一天的取消次数
        cursor.execute("""
            SELECT COUNT(*) AS cancel_count
            FROM Bookings
            WHERE user_id = %s
              AND booking_date = %s
              AND status = 'canceled'
        """, (user_id, booking_date))
        cancel_count_row = cursor.fetchone()
        cancel_count = cancel_count_row['cancel_count'] if cancel_count_row else 0
        print(f"User {user_id} has canceled {cancel_count} bookings on {booking_date}.")

        # 如果用户当天取消次数 >= 3，执行额外逻辑
        if cancel_count >= 3:
            # 给该用户发送一条通知
            cursor.execute("""
                INSERT INTO Notifications (user_id, message, notification_action, status)
                VALUES (%s, %s, 'alert', 'unread')
            """, (
                user_id,
                "You have canceled 3 bookings in one day. Please respect classroom resources."
            ))

            # 直接调用你的发送邮件函数（示例）
            """
            subject = "Blacklisted due to multiple cancellations"
            body = "You have canceled 3 bookings in one day and have been blacklisted for 1 month."
            send_email_to_user(user_id, subject, body)
            """

            # 检查该用户是否已经在黑名单中
            cursor.execute("""
                SELECT blacklist_id
                FROM Blacklist
                WHERE user_id = %s
                  AND end_date >= CURDATE()
            """, (user_id,))
            blacklisted = cursor.fetchone()

            if not blacklisted:
                # 不在黑名单 => 将其加入黑名单（封禁 1 个月）
                admin_id = 1  # 这里示例写死管理员 ID，你可以自行查找或定义
                reason = "Canceled 3 times in one day"

                now = datetime.now()
                end_date = now + timedelta(days=30)  # 封禁 1 个月

                cursor.execute("""
                    INSERT INTO Blacklist (
                        user_id, added_by, added_date, added_time,
                        start_date, start_time, end_date, end_time, reason
                    )
                    VALUES (
                        %s, %s, CURDATE(), CURTIME(),
                        CURDATE(), CURTIME(), %s, %s, %s
                    )
                """, (
                    user_id,
                    admin_id,
                    end_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%H:%M:%S'),
                    reason
                ))

                # 给所有管理员发送通知
                cursor.execute("SELECT user_id FROM Users WHERE role = 'admin'")
                admins = cursor.fetchall()
                for admin in admins:
                    cursor.execute("""
                        INSERT INTO Notifications (user_id, message, notification_action, status)
                        VALUES (%s, %s, 'alert', 'unread')
                    """, (
                        admin['user_id'],
                        f"User {user_id} canceled 3 bookings in one day and has been blacklisted for 1 month."
                    ))

            conn.commit()

        return jsonify({
            "message": "Booking status updated to 'canceled'",
            "booking_id": updated_booking['booking_id'],
            "status": updated_booking['status'],
            "cancel_count": cancel_count,
            "user_id": user_id
        })

    except mysql.connector.Error as e:
        print(f"Database error: {str(e)}")
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        conn.rollback()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


# todo :user id
@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.get_json()
    # if not data or 'user_id' not in data:
    #     return jsonify({"status": "error", "error": "Missing user_id parameter"}), 400

    user_id = get_user_id_by_email()
    print(user_id)

    # # user_id cannot be updated, so delete it from data (also prevent accidental changes if there are other updates)
    # if 'user_id' in data:
    #     data.pop('user_id')

    # get the fields that are allow to update
    update_fields = {}
    for field in ['username', 'email', 'phone_number', 'role']:
        if field in data:
            update_fields[field] = data[field]

    if not update_fields:
        return jsonify({"status": "error", "error": "No update information provided"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        # 先查询当前用户信息
        query_select = "SELECT username, email, phone_number, role FROM Users WHERE user_id = %s"
        cursor.execute(query_select, (user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            return jsonify({"status": "error", "error": "User not found"}), 404

        # 检查更新字段和当前数据的区别
        fields_to_update = {}
        for key, new_value in update_fields.items():
            if current_user[key] != new_value:
                fields_to_update[key] = new_value

        # 如果没有实际变化，提示用户信息未更新
        if not fields_to_update:
            return jsonify({"status": "success", "message": "No changes detected, data remains the same"}), 200

        # 构造动态 SQL 更新语句
        update_clause = ", ".join([f"{field} = %s" for field in fields_to_update.keys()])
        update_values = list(fields_to_update.values())
        update_values.append(user_id)

        query_update = f"UPDATE Users SET {update_clause} WHERE user_id = %s"
        cursor.execute(query_update, tuple(update_values))
        conn.commit()

        return jsonify({"status": "success", "message": "User updated successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# 2. Update existing issue (Admin only)
@app.route('/update-issues/<int:issue_id>', methods=['PUT'])
def update_issue(issue_id):
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取现有问题记录
        cursor.execute("SELECT * FROM Issues WHERE issue_id = %s", (issue_id,))
        raw_issue = cursor.fetchone()

        if not raw_issue:
            conn.close()
            return jsonify({'error': 'Issue not found'}), 404

        # 将元组转换为字典（修复字段访问问题）
        columns = [col[0] for col in cursor.description]
        issue = dict(zip(columns, raw_issue))

        # 准备更新字段
        update_fields = {
            'issue': data.get('issue', issue['issue']),
            'status': data.get('status', issue['status']),
            'start_date': data.get('start_date', issue['start_date']),
            'start_time': data.get('start_time', issue['start_time']),
            'end_date': issue['end_date'],
            'end_time': issue['end_time']
        }

        # 处理状态转换（修复日期调用问题）
        if update_fields['status'] != issue['status']:
            if update_fields['status'] == 'resolved':
                # 使用正确导入的date和datetime对象
                update_fields['end_date'] = date.today().strftime('%Y-%m-%d')  # 直接使用date
                update_fields['end_time'] = datetime.now().strftime('%H:%M:%S')  # 直接使用datetime
            elif issue['status'] == 'resolved' and update_fields['status'] != 'resolved':
                update_fields['end_date'] = None
                update_fields['end_time'] = None

        # 执行更新
        cursor.execute("""
            UPDATE Issues SET
                issue = %s,
                status = %s,
                start_date = %s,
                start_time = %s,
                end_date = %s,
                end_time = %s
            WHERE issue_id = %s
        """, (
            update_fields['issue'],
            update_fields['status'],
            update_fields['start_date'],
            update_fields['start_time'],
            update_fields['end_date'],
            update_fields['end_time'],
            issue_id
        ))

        conn.commit()
        conn.close()
        return jsonify({'message': 'Issue updated successfully'}), 200

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'error': str(e)}), 500


# todo: new function for change unread to read for notification page
@app.route('/update_notification_status', methods=['POST'])
def update_notification_status():
    data = request.get_json()
    notification_id = data.get('notification_id')
    new_status = data.get('status')

    if not notification_id or new_status not in ('read', 'unread'):
        return jsonify(
            {"error": "Missing or invalid parameters — require notification_id and status ('read' or 'unread')"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE Notifications SET status = %s WHERE notification_id = %s"
        cursor.execute(query, (new_status, notification_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Notification not found"}), 404

        return jsonify({
            "message": "Notification status updated successfully",
            "notification_id": notification_id,
            "new_status": new_status
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": "Failed to update notification status", "details": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# ---------------------------- insert ----------------------------


@app.route('/insert_booking', methods=['POST'])
def insert_booking():
    data = request.get_json()
    room_id = data.get('room_id')

    # todo: modify the user_id

    user_id = get_user_id_by_email()
    booking_date = data.get('booking_date')
    start_time = data.get('start_time') + ":00"
    end_time = data.get('end_time') + ":00"
    reason = data.get('reason', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        cursor.execute("SELECT room_type FROM Rooms WHERE room_id = %s", (room_id,))
        room_info = cursor.fetchone()
        if not room_info:
            return jsonify({"status": "error", "error": "Room not found"}), 400
        room_type = room_info[0]

        cursor.execute("""
            SELECT availability_id FROM Room_availability
            WHERE room_id = %s
            AND available_date = %s
            AND available_begin <= %s
            AND available_end >= %s
            AND availability = 0
        """, (room_id, booking_date, start_time, end_time))
        if not cursor.fetchone():
            return jsonify({"status": "error", "error": "The requested time slot is not available"}), 400

        requires_reason = False
        if room_type == 1:
            cursor.execute("""
                SELECT room_trusted_user_id FROM RoomTrustedUsers
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id,))
            room_trusted_user_id = cursor.fetchone()
            cursor.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "error": "User not found"}), 400
            user_role = user[0]
            if user_role not in ('admin', 'professor', 'tutor'):
                if not room_trusted_user_id:
                    requires_reason = True
        elif room_type == 2:
            cursor.execute("""
                SELECT room_trusted_user_id FROM RoomTrustedUsers
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id,))
            if not cursor.fetchone():
                requires_reason = True

        if requires_reason:
            return jsonify({
                "status": "require_reason",
                "message": "Please enter the reason for booking."
            }), 400

        status = 'approved'

        query = """
            INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, room_id, start_time, end_time, booking_date, status, reason))
        conn.commit()


        booking_id = cursor.lastrowid

        return jsonify({
            "status": "success",
            "message": "Booking successful" if status == 'approved' else "Booking request submitted, awaiting approval.",
            "booking_id": booking_id,
            "start_time": start_time,
            "end_time": end_time,
            "booking_date": booking_date,
            "room_id": room_id
        })


            "booking_id": booking_id,
            "start_time": start_time,
            "end_time": end_time,
            "booking_date": booking_date,
            "room_id": room_id

        })
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# todo: add check for the same insert
@app.route('/insert_booking_with_reason', methods=['POST'])
def insert_booking_with_reason():
    """前端输入 reason 后调用此 API 进行最终插入"""
    data = request.get_json()
    room_id = data.get('room_id')

    # 获取当前登录用户的 user_id
    user_id = get_user_id_by_email()
    booking_date = data.get('booking_date')
    start_time = data.get('start_time') + ":00"
    end_time = data.get('end_time') + ":00"
    reason = data.get('reason')

    if not reason.strip():
        return jsonify({"status": "error", "error": "Reason is required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor()

        # 检查是否已有相同的预定记录
        check_query = """
            SELECT * FROM Bookings 
            WHERE room_id = %s AND user_id = %s AND booking_date = %s 

            AND start_time = %s AND end_time = %s AND status IN ('approved', 'pending')

        """
        cursor.execute(check_query, (room_id, user_id, booking_date, start_time, end_time))
        existing_booking = cursor.fetchone()  # 如果有相同的记录，返回结果

        if existing_booking:
            return jsonify({"status": "error", "error": "Duplicate booking, the same booking already exists."}), 400

        # 如果没有重复，执行插入操作
        query = """
            INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status, reason)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
        """
        cursor.execute(query, (user_id, room_id, start_time, end_time, booking_date, reason))
        conn.commit()
        #
        # return jsonify({"status": "success", "message": "Booking request submitted, awaiting approval."})

        booking_id = cursor.lastrowid
        return jsonify({
            "status": "success",
            "message": "Booking request submitted, awaiting approval.",
            "booking_id": booking_id
        })
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


@app.route('/insert_room', methods=['POST'])
def insert_room():
    data = request.get_json()
    room_name = data['room_name']
    capacity = data['capacity']
    equipment = data['equipment']
    location = data['location']
    room_type = data['room_type']
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Rooms (room_name, capacity, equipment, location,room_type)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (room_name, capacity, equipment, location, room_type))
        conn.commit()
        return jsonify({"status": "success", "message": "Room inserted successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# todo: add- check if the user_id is the same
@app.route('/insert-blacklist', methods=['POST'])
def add_to_blacklist():
    """
    向 Blacklist 表插入一条新的记录。
    示例请求体（JSON）:
    {
        "user_id": 2,           # 要被加入黑名单的目标用户
        "start_date": "2025-03-20",
        "start_time": "09:00",
        "end_date": "2025-03-22",
        "end_time": "18:00",
        "reason": "Violation of rules"
    }
    注意：added_by 将由当前登录用户自动获取
    """
    try:
        data = request.json

        # 前端传入要被黑名单的用户ID
        user_id = data.get('user_id')
        # 获取当前登录用户的ID，作为 added_by
        print("Session info at /insert-blacklist:", session)
        added_by = get_user_id_by_email()
        print("added_by:", added_by)
        start_date_str = data.get('start_date')
        start_time_str = data.get('start_time')
        end_date_str = data.get('end_date')
        end_time_str = data.get('end_time')
        reason = data.get('reason')

        # 检查必要字段
        if not all([user_id, added_by, start_date_str, start_time_str, end_date_str, end_time_str]):
            return jsonify({"error": "Missing required fields"}), 400

        # 如果目标用户和当前用户相同，则不允许（防止自己加入自己的黑名单）
        if user_id == added_by:
            return jsonify({"error": "You cannot add yourself to the blacklist."}), 400

        # 格式化日期和时间
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError as e:
            return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400

        # 设置记录添加的日期和时间
        added_date = date.today()
        added_time = datetime.now().time()

        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. 检查目标用户是否存在于 Users 表中
        cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
        target_user = cursor.fetchone()
        if not target_user:
            return jsonify({"error": "Target user does not exist"}), 400

        # 2. 检查该目标用户是否已经在黑名单中
        check_query = "SELECT * FROM Blacklist WHERE user_id = %s"
        cursor.execute(check_query, (user_id,))
        existing_blacklist_entry = cursor.fetchall()  # 使用 fetchall 确保读取所有结果

        if existing_blacklist_entry:
            # 如果该用户已经在黑名单中
            return jsonify({"error": "User is already in the blacklist"}), 400

        # 3. 执行插入操作
        insert_query = """
            INSERT INTO Blacklist
            (user_id, added_by, added_date, added_time, start_date, start_time, end_date, end_time, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            user_id,
            added_by,
            added_date,
            added_time,
            start_date,
            start_time,
            end_date,
            end_time,
            reason
        ))
        conn.commit()

        blacklist_id = cursor.lastrowid

        return jsonify({
            "message": "New blacklist entry created successfully",
            "blacklist_id": blacklist_id,
            "user_id": user_id,
            "added_by": added_by,
            "added_date": added_date.strftime("%Y-%m-%d"),
            "added_time": added_time.strftime("%H:%M:%S"),
            "start_date": start_date_str,
            "start_time": start_time_str,
            "end_date": end_date_str,
            "end_time": end_time_str,
            "reason": reason
        }), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


@app.route('/insert_trusted_user', methods=['POST'])
def insert_trusted_user():
    data = request.get_json()
    room_id = data['room_id']
    user_id = data['user_id']
    added_by = get_user_id_by_email()
    # 如果前端没有传入日期和时间，可以考虑自动生成当前日期和时间
    added_date = data.get('added_date')  # 格式应为 'YYYY-MM-DD'
    added_time = data.get('added_time')  # 格式应为 'HH:MM:SS'
    notes = data.get('notes', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. 检查 user_id 是否存在
        cursor.execute("SELECT COUNT(*) AS cnt FROM Users WHERE user_id = %s", (user_id,))
        user_count = cursor.fetchone()['cnt']
        if user_count == 0:
            return jsonify({"status": "error", "error": f"User with user_id={user_id} does not exist."}), 400

        # 2. 检查 room_id 是否存在
        cursor.execute("SELECT COUNT(*) AS cnt FROM Rooms WHERE room_id = %s", (room_id,))
        room_count = cursor.fetchone()['cnt']
        if room_count == 0:
            return jsonify({"status": "error", "error": f"Room with room_id={room_id} does not exist."}), 400

        # 3. 检查该用户是否已在该房间的受信任名单中
        check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(check_query, (room_id, user_id))
        existing = cursor.fetchone()
        if existing:
            return jsonify({
                "status": "error",
                "error": "The user is already in the trusted user list for this room."
            }), 400

        # 4. 如果不存在则执行插入操作
        query = """
            INSERT INTO RoomTrustedUsers (room_id, user_id, added_by, added_date, added_time, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (room_id, user_id, added_by, added_date, added_time, notes))
        conn.commit()

        return jsonify({"status": "success", "message": "Trusted user added successfully!"})

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# @app.route('/insert_trusted_user', methods=['POST'])
# def insert_trusted_user():
#     data = request.get_json()
#     room_id = data['room_id']
#     user_id = data['user_id']
#     added_by = get_user_id_by_email()
#     # 如果前端没有传入日期和时间，可以考虑自动生成当前日期和时间
#     added_date = data.get('added_date')  # 格式应为 'YYYY-MM-DD'
#     added_time = data.get('added_time')  # 格式应为 'HH:MM:SS'
#     notes = data.get('notes', '')

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"status": "error", "error": "Database connection failed"}), 500
#     try:
#         # 使用字典格式返回结果
#         cursor = conn.cursor(dictionary=True)

#         # 先检查该用户是否已在该房间的受信任名单中
#         check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
#         cursor.execute(check_query, (room_id, user_id))
#         existing = cursor.fetchone()
#         if existing:
#             return jsonify(
#                 {"status": "error", "error": "The user is already in the trusted user list for this room."}), 400

#         # 如果不存在则执行插入操作
#         query = """
#         INSERT INTO RoomTrustedUsers (room_id, user_id, added_by, added_date, added_time, notes)
#         VALUES (%s, %s, %s, %s, %s, %s)
#         """
#         cursor.execute(query, (room_id, user_id, added_by, added_date, added_time, notes))
#         conn.commit()
#         return jsonify({"status": "success", "message": "Trusted user added successfully!"})
#     except mysql.connector.Error as err:
#         conn.rollback()
#         return jsonify({"status": "error", "error": str(err)}), 400
#     finally:
#         if conn:
#             conn.close()


# 1. Insert new issue (Admin only)
@app.route('/insert-issues', methods=['POST'])
def add_issue():
    try:
        data = request.get_json()
        required_fields = ['room_id', 'issue', 'start_date', 'start_time']

        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get admin user_id by email
        admin_id = get_user_id_by_email()
        if not admin_id:
            return jsonify({'error': 'Admin user not found'}), 404

        # Check room existence
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查房间是否存在
        cursor.execute("SELECT room_id FROM Rooms WHERE room_id = %s", (data['room_id'],))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Room not found'}), 404

        # Insert new issue with correct status
        cursor.execute("""
            INSERT INTO Issues (
                room_id, 
                issue, 
                status, 
                start_date, 
                start_time, 
                added_by
            ) VALUES (
                %s, %s, DEFAULT, %s, %s, %s
            )
        """, (
            data['room_id'],
            data['issue'],
            data['start_date'],
            data['start_time'],
            admin_id
        ))

        conn.commit()
        new_issue_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'message': 'Issue created successfully',
            'issue_id': new_issue_id
        }), 201

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/insert_users_admin', methods=['POST'])
def insert_use_adminr():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Required fields (user_id excluded)
    required = ["username", "email", "phone_number", "role"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": "Missing required fields", "missing_fields": missing}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    phone = data["phone_number"].strip()
    role = data["role"].strip()

    # Validate role value
    if role not in ("admin", "professor", "student", "tutor"):
        return jsonify({"error": f"Invalid role '{role}'"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for duplicate email
        cursor.execute("SELECT 1 FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered"}), 409

        # Insert new user
        cursor.execute(
            "INSERT INTO Users (username, email, phone_number, role) VALUES (%s, %s, %s, %s)",
            (username, email, phone, role)
        )
        conn.commit()

        return jsonify({
            "message": "User created successfully",
            "user_id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    finally:
        cursor.close()
        conn.close()


# -------------------------initialize room avalibility--------------------
# Define room time slots (available time slots for each room)
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


# Function to insert room availability data
@app.route('/insert_room_availability', methods=['GET'])
def insert_room_availability():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Get all room_ids
    cursor.execute("SELECT room_id FROM Rooms")
    rooms = cursor.fetchall()

    # Get today's date and calculate all dates for this week (from Monday to Sunday)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday's date this week
    dates_this_week = [start_of_week + timedelta(days=i) for i in range(7)]  # All 7 days of the week

    # Insert room availability records for each room and time slot
    try:
        for room in rooms:
            room_id = room[0]

            # Insert records for each time slot and date for the current room
            for start_time, end_time in availability_times:
                for date in dates_this_week:
                    cursor.execute("""
                        INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability)
                        VALUES (%s, %s, %s, %s, 0)  -- Set availability to 0 (not available)
                    """, (room_id, start_time, end_time, date.strftime('%Y-%m-%d')))

        # Commit transaction
        connection.commit()
        return jsonify({"message": "Room availability records have been successfully inserted!"}), 200

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # Close database connection
        cursor.close()
        connection.close()


# -----------------------------------update room availibility-------------------------

# ============================ Utility Functions ============================
def get_week_dates():
    """Calculate the dates for each day of the current week (from Monday to Sunday)"""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ============================ Global Variables ============================
# Initialize timetable: 7 columns represent Sunday (index 0) to Saturday (index 6)
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# Mapping of class periods to time ranges (do not modify)
class_periods = {
    "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
    "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
    "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
    "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
    "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
    "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
}

# Regular expression to extract classroom names (e.g., "Foreign Language Network Building 635")
classroom_pattern = re.compile(r'外语网络楼(\d{3})')


def extract_classrooms(course_text):
    """Extract classroom names from course text"""
    return classroom_pattern.findall(course_text)


# Read CSV file and store week-to-date mapping
def load_weeks(file_path):
    weeks = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            week = {
                "week_number": int(row['week_number']),
                "start_date": datetime.strptime(row['start_date'], "%Y-%m-%d"),
                "end_date": datetime.strptime(row['end_date'], "%Y-%m-%d")
            }
            weeks.append(week)
    return weeks


# Calculate which week the current date belongs to
def get_current_week(weeks):
    current_date = datetime.today()
    for week in weeks:
        if week["start_date"] <= current_date <= week["end_date"]:
            return week["week_number"]
    return None  # If the date is not within any week


# ============================ Data Scraping Functionality (Keep unchanged) ============================
def crawl_data():
    """Scrape data for majors, classes, and schedules for each academic year"""
    global timetable  # Use global timetable
    class_usage = {}
    session = requests.Session()
    url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url_main
    }
    session.get(url_main, headers=headers)
    current_date = datetime.today().date()
    # Get the current year
    current_year = current_date.today().year
    # Read the current week from the file
    weeks = load_weeks('weeks.csv')
    current_week = get_current_week(weeks)
    # Check if the current date is before September 1st
    if current_date.month < 9 or (current_date.month == 9 and current_date.day < 1):
        # If the date is before September 1st, academic_years do not include the current year
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year)]
    else:
        # If the date is after September 1st, academic_years include the current year
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year + 1)]

    if (current_date.month >= 9 and current_date.month <= 12):
        # If the current date is between September 1st and February 1st next year
        semester_id = f"{current_year}-{current_year + 1}-1"
    elif (current_date.month == 1):
        semester_id = f"{current_year - 1}-{current_year}-1"
    elif (current_date.month >= 2 and current_date.month <= 8):
        # If the current date is between February 2nd and August 31st
        semester_id = f"{current_year - 1}-{current_year}-2"
    url_major = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
    url_class = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

    for year in academic_years:
        major_data = {"yxbh": "tc9qn3Xixg", "rxnf": year}
        response_major = session.post(url_major, data=major_data, headers=headers)
        if response_major.status_code != 200 or not response_major.text.strip():
            continue
        fixed_json_major = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_major.text)
        fixed_json_major = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_major)
        try:
            major_list = json.loads(fixed_json_major)
        except json.JSONDecodeError:
            continue

        for major in major_list:
            major_id = major["jx01id"]
            class_data = {"yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id, "xnxq01id": semester_id}
            response_class = session.post(url_class, data=class_data, headers=headers)
            if response_class.status_code != 200 or not response_class.text.strip():
                continue
            fixed_json_class = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_class.text)
            fixed_json_class = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_class)
            try:
                class_list = json.loads(fixed_json_class)
            except json.JSONDecodeError:
                continue

            for class_info in class_list:
                class_id = class_info["xx04id"]
                class_name = class_info["bj"]
                schedule_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
                schedule_data = {
                    "type": "xx04",
                    "isview": "1",
                    "xx04id": class_id,
                    "yxbh": "tc9qn3Xixg",
                    "rxnf": year,
                    "zy": major_id,
                    "bjbh": class_name,
                    "zc": current_week,
                    "xnxq01id": semester_id,
                    "xx04mc": "",
                    "sfFD": "1"
                }
                response_schedule = session.post(schedule_url, data=schedule_data, headers=headers)
                if response_schedule.status_code != 200 or not response_schedule.text.strip():
                    continue
                soup = BeautifulSoup(response_schedule.text, "html.parser")
                table = soup.find("table")
                if table:
                    rows = table.find_all("tr")[1:]
                    for row_idx, row in enumerate(rows):
                        cols = row.find_all("td")
                        if len(cols) < 2:
                            continue
                        time_period = list(timetable.keys())[row_idx]
                        for col_idx in range(1, 8):
                            if col_idx >= len(cols):
                                continue
                            room_text = cols[col_idx].text.strip()
                            if not room_text:
                                continue
                            rooms = extract_classrooms(room_text)
                            if rooms:
                                if timetable[time_period][col_idx - 1]:
                                    timetable[time_period][col_idx - 1] += ", " + ", ".join(rooms)
                                else:
                                    timetable[time_period][col_idx - 1] = ", ".join(rooms)
                                for room in rooms:
                                    if room not in class_usage:
                                        class_usage[room] = []
                                    class_usage[room].append(f"周{col_idx} {time_period}")
    return class_usage


# ============================ Data Integration ============================
def integrate_schedule(class_usage):
    classroom_schedule = {}
    for room, times in class_usage.items():
        time_slots = sorted(set(times))
        days_schedule = {i: [] for i in range(7)}
        for time in time_slots:
            day, period = time.split(" ")
            day_number = int(day[1]) - 1
            time_ranges = class_periods.get(period, [("Unknown Time", "Unknown Time")])
            for time_range in time_ranges:
                start_time, end_time = time_range
                days_schedule[day_number].append(f"{start_time}{end_time}")
        formatted_schedule = {}
        for day_idx in range(7):
            if days_schedule[day_idx]:
                formatted_schedule[day_idx] = sorted(days_schedule[day_idx])
        classroom_schedule[int(room)] = formatted_schedule

    room_2d_array = {}
    for room, schedule in classroom_schedule.items():
        room_2d_array[room] = [[""] * len(class_periods) for _ in range(7)]
        for day_idx, times in schedule.items():
            for time_idx, time in enumerate(times):
                room_2d_array[room][day_idx][time_idx] = time
    return room_2d_array


def format_schedule_data(new_room_2d_array):
    week_dates = get_week_dates()
    formatted_schedule = []
    for room, schedule in new_room_2d_array.items():
        for day_idx, day in enumerate(schedule):
            for time_slot in day:
                if time_slot:
                    start_time, end_time = time_slot.split("-")
                    formatted_schedule.append([room, week_dates[day_idx], start_time, end_time])
    return formatted_schedule


# ============================ Update Database ============================
def update_room_availability(formatted_schedule):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        for entry in formatted_schedule:
            room_name, available_date, available_begin, available_end = entry  # Unpack data
            cursor.execute("SELECT room_id FROM Rooms WHERE room_name = %s", (room_name,))
            room_result = cursor.fetchone()
            if not room_result:
                continue
            room_id = room_result["room_id"]
            cursor.execute(""" 
                SELECT availability_id FROM Room_availability 
                WHERE room_id = %s AND available_date = %s 
                AND available_begin = %s AND available_end = %s
            """, (room_id, available_date, available_begin, available_end))
            existing_availability = cursor.fetchone()
            if existing_availability:
                cursor.execute("""
                    UPDATE Room_availability 
                    SET availability = 1 
                    WHERE availability_id = %s
                """, (existing_availability["availability_id"],))
            else:
                cursor.execute("""
                    INSERT INTO Room_availability (room_id, available_date, available_begin, available_end, availability)
                    VALUES (%s, %s, %s, %s, 1)
                """, (room_id, available_date, available_begin, available_end))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ============================ Split Time Slots ============================
def split_time_slots(data):
    """Split stored string data into individual time slots (remove all brackets)"""
    new_data = {}
    for room, schedule in data.items():
        new_schedule = []
        for day in schedule:
            new_day = []
            for item in day:
                if item:
                    time_slots = item.split('][')
                    if len(time_slots) > 1:
                        for slot in time_slots:
                            clean_slot = slot.replace("[", "").replace("]", "")
                            new_day.append(clean_slot)
                    else:
                        new_day.append(item)
                else:
                    new_day.append('')  # Handle empty values
            new_schedule.append(new_day)
        new_data[room] = new_schedule
    return new_data


# ============================ Flask API Endpoint ============================
@app.route('/run_scheduler', methods=['GET'])
def run_scheduler():
    try:
        # Run the scraping and database update process
        result = main_scheduler()
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================ Main Scheduler Function ============================
def main_scheduler():
    # 1. Scrape data
    class_usage = crawl_data()
    # 2. Integrate data into 2D array
    room_2d_array = integrate_schedule(class_usage)
    # 3. Split time slots and remove brackets
    new_room_2d_array = split_time_slots(room_2d_array)
    # 4. Format data and generate the standard format list
    formatted_schedule = format_schedule_data(new_room_2d_array)
    # 5. Update database
    update_room_availability(formatted_schedule)
    return "Crawling and updating database successfully!"


if __name__ == '__main__':
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"→ {rule}")
    # 启用 HTTPS
    app.run(
        host='0.0.0.0',  # 监听所有网络接口
        port=8000,  # HTTPS 默认端口
        ssl_context=('diicsu.top.pem', 'diicsu.top.key')  # 证书和私钥文件
    )

# if __name__ == '__main__':
#     print("\nRegistered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"→ {rule}")
#     app.run(host='0.0.0.0', port=8000, debug=True)
