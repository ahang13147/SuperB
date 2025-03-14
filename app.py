#  @version: 3/12/2025
#  @author: Xin Yu, Siyan Guo, Zibang Nie
# add: finished-workflow-booking get api
from contextlib import closing

from flask import Flask, redirect, request, session, url_for, render_template, jsonify
from flask_cors import CORS
import mysql.connector
import requests
# from bs4 import BeautifulSoup
# import json
# import re
# import time
from datetime import date, datetime, timedelta
import yaml
import msal

app = Flask(__name__)
CORS(app)  # 允许所有来源访问
app.secret_key = 'your-secret-key-here'


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


# ---------------------------- login ----------------------------


@app.route('/')
def index():
    return redirect(url_for('login_page'))


@app.route('/login')
def login_page():
    return '''
    <script>
        window.location.href = "/auth";
    </script>
    '''


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


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


# @app.route('/profile')
# def profile():
#     # 显示用户信息
#     if 'access_token' not in session:
#         return redirect(url_for('index'))
#
#     headers = {'Authorization': f'Bearer {session["access_token"]}'}
#     user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()
#
#     # 渲染本地HTML文件并传递用户信息
#     return render_template(
#         'booking_centre.html',
#         name=user_info.get('displayName', '未知用户'),
#         email=user_info.get('mail', '无邮箱信息'),
#         id=user_info.get('id', '')
#     )

# @app.route('/user_profile')
# def booking_centre():
#     return render_template('user_profile.html')


#路由：渲染 booking_centre.html
@app.route('/booking_centre')
def booking_centre():
    return render_template('booking_centre.html')


@app.route('/my_reservation')
def my_reservation():
    return render_template('my_reservation.html')


@app.route('/user_profile')
def user_profile():
    return render_template('user_profile.html')


@app.route('/my_notification')
def my_notification():
    return render_template('my_notification.html')


@app.route('/error')
def error_page():
    return render_template('error.html')  # 确保 templates/error.html 文件存在


@app.route('/adminSidebar')
def adminSidebar():
    return render_template('adminSidebar.html')


@app.route('/Approval_Center')
def Approval_Center():
    return render_template('Approval_Center.html')


@app.route('/blacklist')
def blacklist():
    return render_template('blacklist.html')


@app.route('/booking_centre_admin')
def booking_centre_admin():
    return render_template('booking_centre_admin.html')


@app.route('/cancel_reservation')
def cancel_reservation():
    return render_template('cancel_reservation.html')


@app.route('/my_profile_admin')
def my_profile_admin():
    return render_template('my_profile_admin.html')


@app.route('/my_reservation_admin')
def my_reservation_admin():
    return render_template('my_reservation_admin.html')


@app.route('/notice_admin')
def notice_admin():
    return render_template('notice_admin.html')


@app.route('/room_management')
def room_management():
    return render_template('room_management.html')


@app.route('/trust_list')
def trust_list():
    return render_template('trust_list.html')


# 路由：渲染 login.html
@app.route('/login')
def login():
    return render_template('login.html')


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

    # 获取用户 email
    user_email = user_info.get('mail') or user_info.get('userPrincipalName')
    if not user_email:
        print("No email or userPrincipalName in Microsoft response")
        return redirect(url_for('error_page'))

    session['user_email'] = user_email

    try:
        print(f"Calling role API with email: {user_email}")
        role_response = requests.get(
            f"http://localhost:8000/login_get_role?email={user_email}"  # 参数名改为 email
        )
        print(f"Role API response status: {role_response.status_code}, body: {role_response.text}")

        if role_response.status_code == 200:
            role_data = role_response.json()
            user_role = role_data.get('role', 'user')
            session['user_role'] = user_role

            # 根据角色重定向
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
        with closing(get_db_connection()) as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT role FROM Users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if user:
                    return jsonify({'role': user['role']})
                else:
                    return jsonify({"error": "User not found"}), 404

    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------- delete ----------------------------
@app.route('/delete/users', methods=['POST'])
def delete_users():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    role = data.get('role')
    # 使用同一数据库连接和事务，先删除依赖于该用户的记录，再删除用户记录
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if user_id:
            # 1. 删除该用户的通知记录
            cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
            # 2. 删除该用户预订的记录，其审批记录依赖于预订（先删除审批记录）
            cursor.execute("""
                DELETE FROM Approvals 
                WHERE booking_id IN (
                    SELECT booking_id FROM Bookings WHERE user_id = %s
                )
            """, (user_id,))
            # 删除该用户的预订记录
            cursor.execute("DELETE FROM Bookings WHERE user_id = %s", (user_id,))
            # 3. 删除审批记录中，该用户作为管理员审批的记录
            cursor.execute("DELETE FROM Approvals WHERE admin_id = %s", (user_id,))
            # 4. 删除该用户生成的报告
            cursor.execute("DELETE FROM Reports WHERE admin_id = %s", (user_id,))
        # 删除用户记录
        query = """
        DELETE FROM Users
        WHERE (user_id = %s OR %s IS NULL)
          AND (username = %s OR %s IS NULL)
          AND (email = %s OR %s IS NULL)
          AND (role = %s OR %s IS NULL)
        """
        params = (user_id, user_id, username, username, email, email, role, role)
        cursor.execute(query, params)
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


@app.route('/delete/rooms', methods=['POST'])
def delete_rooms():
    data = request.json
    room_id = data.get('room_id')
    room_name = data.get('room_name')
    capacity = data.get('capacity')
    location = data.get('location')
    # 先删除依赖数据：Room_availability、Bookings（依赖该房间）
    dependent_queries = [
        ("DELETE FROM Room_availability WHERE room_id = %s", (room_id,)),
        ("DELETE FROM Bookings WHERE room_id = %s", (room_id,))
    ]
    for q, p in dependent_queries:
        delete_record(q, p)
    query = """
    DELETE FROM Rooms
    WHERE (room_id = %s OR %s IS NULL)
      AND (room_name = %s OR %s IS NULL)
      AND (capacity = %s OR %s IS NULL)
      AND (location = %s OR %s IS NULL)
    """
    params = (room_id, room_id, room_name, room_name, capacity, capacity, location, location)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/room_availability', methods=['POST'])
def delete_room_availability():
    data = request.json
    room_id = data.get('room_id')
    available_date = data.get('available_date')
    available_begin = data.get('available_begin')
    available_end = data.get('available_end')
    query = """
    DELETE FROM Room_availability
    WHERE (room_id = %s OR %s IS NULL)
      AND (available_date = %s OR %s IS NULL)
      AND (available_begin = %s OR %s IS NULL)
      AND (available_end = %s OR %s IS NULL)
    """
    params = (
        room_id, room_id, available_date, available_date, available_begin, available_begin, available_end,
        available_end)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/approvals', methods=['POST'])
def delete_approvals():
    data = request.json
    approval_id = data.get('approval_id')
    booking_id = data.get('booking_id')
    admin_id = data.get('admin_id')
    approval_status = data.get('approval_status')
    query = """
    DELETE FROM Approvals
    WHERE (approval_id = %s OR %s IS NULL)
      AND (booking_id = %s OR %s IS NULL)
      AND (admin_id = %s OR %s IS NULL)
      AND (approval_status = %s OR %s IS NULL)
    """
    params = (approval_id, approval_id, booking_id, booking_id, admin_id, admin_id, approval_status, approval_status)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/notifications', methods=['POST'])
def delete_notifications():
    data = request.json
    notification_id = data.get('notification_id')
    user_id = data.get('user_id')
    notification_type = data.get('notification_type')
    status_val = data.get('status')
    query = """
    DELETE FROM Notifications
    WHERE (notification_id = %s OR %s IS NULL)
      AND (user_id = %s OR %s IS NULL)
      AND (notification_type = %s OR %s IS NULL)
      AND (status = %s OR %s IS NULL)
    """
    params = (
        notification_id, notification_id, user_id, user_id, notification_type, notification_type, status_val,
        status_val)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/reports', methods=['POST'])
def delete_reports():
    data = request.json
    report_id = data.get('report_id')
    admin_id = data.get('admin_id')
    report_type = data.get('report_type')
    query = """
    DELETE FROM Reports
    WHERE (report_id = %s OR %s IS NULL)
      AND (admin_id = %s OR %s IS NULL)
      AND (report_type = %s OR %s IS NULL)
    """
    params = (report_id, report_id, admin_id, admin_id, report_type, report_type)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/notifications_by_user', methods=['POST'])
def delete_notifications_by_user():
    data = request.json
    user_id = data.get('user_id')
    query = "DELETE FROM Notifications WHERE user_id = %s"
    params = (user_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/approvals_by_booking', methods=['POST'])
def delete_approvals_by_booking():
    data = request.json
    booking_id = data.get('booking_id')
    query = "DELETE FROM Approvals WHERE booking_id = %s"
    params = (booking_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


@app.route('/delete/room_availability_by_room', methods=['POST'])
def delete_room_availability_by_room():
    data = request.json
    room_id = data.get('room_id')
    query = "DELETE FROM Room_availability WHERE room_id = %s"
    params = (room_id,)
    result, status = delete_record(query, params)
    return jsonify({"message": result}), status


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
                r.room_id, r.room_name, r.capacity, r.equipment, r.location,r.room_type,
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
                b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time, b.status,
                r.room_name, r.location, r.capacity, r.equipment
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
            ORDER BY b.booking_date, b.start_time
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
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                b.booking_id, b.user_id, b.room_id, b.booking_date, b.start_time, b.end_time, b.status, b.reason,
                r.room_name, r.location, r.capacity, r.equipment
            FROM Bookings b
            JOIN Rooms r ON b.room_id = r.room_id
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
            SELECT room_id, room_name, capacity, equipment, location
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

        # SQL 查询，获取状态为 'pending' 的预定记录，并连接 Users 和 Rooms 表
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,b.status,
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

        # SQL 查询，获取状态为 'pending' 的预定记录，并连接 Users 和 Rooms 表
        query = """
            SELECT 
                b.booking_id, b.booking_date, b.start_time, b.end_time, b.reason,b.status,
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


@app.route('/get_user', methods=['POST'])
def get_user():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"status": "error", "error": "Missing user_id parameter"}), 400

    user_id = data['user_id']
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


# ---------------------------- update ----------------------------

@app.route('/update-room/<int:room_id>', methods=['PUT'])
def update_room(room_id):
    print(f"Received PUT request to update room with ID: {room_id}")
    data = request.json
    print(f"Request body: {data}")
    room_name = data.get('room_name')
    capacity = data.get('capacity')
    equipment = data.get('equipment')
    location = data.get('location')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve existing room data by room_id
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        existing_room = cursor.fetchone()
        if not existing_room:
            print(f"No room found with ID {room_id}.")
            return jsonify({"error": "Room not found"}), 404

        # Check if the new data is exactly the same as the existing data.
        # Assuming the order of fields is: room_id, room_name, capacity, equipment, location.
        if (room_name == existing_room[1] and
                capacity == existing_room[2] and
                equipment == existing_room[3] and
                location == existing_room[4]):
            print("No changes detected.")
            return jsonify({"message": "No changes were made"}), 200

        # Check for duplicate room name in other records.
        cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
        duplicate_room = cursor.fetchone()
        if duplicate_room:
            print(f"Room name '{room_name}' already exists.")
            return jsonify({"error": "Room name already exists"}), 400

        # Proceed with update if there are changes.
        update_query = """
            UPDATE Rooms
            SET room_name = %s, capacity = %s, equipment = %s, location = %s
            WHERE room_id = %s
        """
        update_params = (room_name, capacity, equipment, location, room_id)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()

        # In rare cases if rowcount is still 0 (but we already checked), we can respond accordingly.
        if cursor.rowcount == 0:
            print(f"No changes were made during update for room id {room_id}.")
            return jsonify({"message": "No changes were made"}), 200

        # Return the updated room data.
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        updated_room = cursor.fetchone()
        print(f"Updated room: {updated_room}")
        return jsonify({
            "message": "Room updated successfully",
            "room_id": updated_room[0],
            "room_name": updated_room[1],
            "capacity": updated_room[2],
            "equipment": updated_room[3],
            "location": updated_room[4]
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

        # 提交事务
        conn.commit()

        # 查询更新后的预定信息
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        return jsonify({
            "message": f"Booking status updated to {updated_booking['status']}",
            "booking_id": updated_booking['booking_id'],
            "status": updated_booking['status']
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
        cursor = conn.cursor()

        # 查找待取消的预定记录
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s AND status != 'canceled'", (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            print(f"No booking found with ID {booking_id} or the booking is already canceled.")
            return jsonify({"error": "Booking not found or already canceled"}), 404

        # 更新该预定的 status 为 'canceled'
        update_query = """
            UPDATE Bookings
            SET status = 'canceled'
            WHERE booking_id = %s
        """
        update_params = (booking_id,)
        print(f"Executing update query: {update_query} with parameters: {update_params}")
        cursor.execute(update_query, update_params)
        conn.commit()

        if cursor.rowcount == 0:
            print(f"Failed to cancel booking with ID {booking_id}.")
            return jsonify({"error": "Failed to cancel booking"}), 500

        # 获取更新后的预定信息
        cursor.execute("SELECT * FROM Bookings WHERE booking_id = %s", (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        return jsonify({
            "message": "Booking status updated to 'canceled'",
            "booking_id": updated_booking[0],
            "status": updated_booking[6]  # Assuming status is the 6th column in Bookings table
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


@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({"status": "error", "error": "Missing user_id parameter"}), 400

    user_id = data['user_id']

    # 不能更新 user_id，所以将其从 data 中删除（如果存在其他更新项时也防止意外更改）
    if 'user_id' in data:
        data.pop('user_id')

    # 提取允许更新的字段
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


# ---------------------------- insert ----------------------------

@app.route('/insert_booking', methods=['POST'])
def insert_booking():
    data = request.get_json()
    room_id = data.get('room_id')
    user_id = data.get('user_id')
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
            cursor.execute("SELECT role FROM Users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({"status": "error", "error": "User not found"}), 400
            user_role = user[0]
            if user_role not in ('admin', 'professor', 'tutor'):
                requires_reason = True
        elif room_type == 2:
            cursor.execute("""
                SELECT room_trusted_user_id FROM RoomTrustedUsers 
                WHERE room_id = %s AND user_id = %s
            """, (room_id, user_id))
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

        return jsonify({
            "status": "success",
            "message": "Booking successful" if status == 'approved' else "Booking request submitted, awaiting approval."
        })

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


@app.route('/insert_booking_with_reason', methods=['POST'])
def insert_booking_with_reason():
    """前端输入 reason 后调用此 API 进行最终插入"""
    data = request.get_json()
    room_id = data.get('room_id')
    user_id = data.get('user_id')
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

        query = """
            INSERT INTO Bookings (user_id, room_id, start_time, end_time, booking_date, status, reason)
            VALUES (%s, %s, %s, %s, %s, 'pending', %s)
        """
        cursor.execute(query, (user_id, room_id, start_time, end_time, booking_date, reason))
        conn.commit()

        return jsonify({"status": "success", "message": "Booking request submitted, awaiting approval."})

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
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO Rooms (room_name, capacity, equipment, location)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (room_name, capacity, equipment, location))
        conn.commit()
        return jsonify({"status": "success", "message": "Room inserted successfully!"})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


@app.route('/insert-blacklist', methods=['POST'])
def add_to_blacklist():
    """
    向 Blacklist 表插入一条新的记录。
    示例请求体（JSON）:
    {
        "user_id": 2,
        "added_by": 1,
        "start_date": "2025-03-20",
        "start_time": "09:00",
        "end_date": "2025-03-22",
        "end_time": "18:00",
        "reason": "Violation of rules"
    }
    """
    try:
        data = request.json

        user_id = data.get('user_id')
        added_by = data.get('added_by')
        start_date_str = data.get('start_date')
        start_time_str = data.get('start_time')
        end_date_str = data.get('end_date')
        end_time_str = data.get('end_time')
        reason = data.get('reason')

        if not all([user_id, added_by, start_date_str, start_time_str, end_date_str, end_time_str]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            end_time = datetime.strptime(end_time_str, "%H:%M").time()
        except ValueError as e:
            return jsonify({"error": f"Invalid date/time format: {str(e)}"}), 400

        added_date = date.today()
        added_time = datetime.now().time()

        conn = get_db_connection()
        cursor = conn.cursor()

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


@app.route('/insert_trusted_user', methods=['POST'])
def insert_trusted_user():
    data = request.get_json()
    room_id = data['room_id']
    user_id = data['user_id']
    added_by = data['added_by']
    # 如果前端没有传入日期和时间，可以考虑自动生成当前日期和时间
    added_date = data.get('added_date')  # 格式应为 'YYYY-MM-DD'
    added_time = data.get('added_time')  # 格式应为 'HH:MM:SS'
    notes = data.get('notes', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500
    try:
        # 使用字典格式返回结果
        cursor = conn.cursor(dictionary=True)

        # 先检查该用户是否已在该房间的受信任名单中
        check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(check_query, (room_id, user_id))
        existing = cursor.fetchone()
        if existing:
            return jsonify(
                {"status": "error", "error": "The user is already in the trusted user list for this room."}), 400

        # 如果不存在则执行插入操作
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


# if __name__ == '__main__':
#     print("\nRegistered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"→ {rule}")
#     app.run(debug=True)

if __name__ == '__main__':
    print("\nRegistered routes:")
    for rule in app.url_map.iter_rules():
        print(f"→ {rule}")
    app.run(host='0.0.0.0', port=8000, debug=True)
