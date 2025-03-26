# -*- coding: utf-8 -*-
"""
Author: Zibang Nie
Description: This Flask application sends reminder emails to users about their room bookings.
             It retrieves booking details from the database and sends an email to the user.
             The email includes booking details such as room name, location, start time, and end time.
             Each endpoint is responsible for sending a specific type of email based on the booking status.
             The response to each request is a JSON object containing the status of the email operation and the booking_id.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_mail import Mail, Message
import mysql.connector
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from multiprocessing import Process

app = Flask(__name__)

# Configuration for Flask application
app.secret_key = 'your_secret_key'
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',  # Email server
    'MAIL_PORT': 587,              # Port (587 for TLS)
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': '2530681892@qq.com',  # Sender's email
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',    # Sender's email password
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')  # Default sender
})

mail = Mail(app)

# Database connection settings
db_config = {
    'host': 'localhost',  # Database host
    'user': 'root',  # Database username
    'password': '1234',  # Database password
    'database': 'booking_system_db'  # Database name
}

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
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            ssl_disabled=True
        )
        cursor = conn.cursor()

        query = "SELECT username, email FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0], result[1]  # username, email
        else:
            print(f"User ID {user_id} not found.")
            return None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None


def send_email(to_email, subject, body):
    """
    Send an email to the specified recipient.

    Args:
        to_email (str): Recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.
    """
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


# def broadcast_email_to_all_administrators(subject, body):
#     """
#     Launch email broadcasting in a separate process to avoid blocking the main thread.
#     """
#     process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
#     process.start()

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
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404

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
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404

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
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404

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
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404

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
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


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
    if not data or 'content' not in data:
        return jsonify({'status': 'failed', 'message': 'Failed to get content'}), 400


    content = str(data.get('message'))

    subject = f"Private_message from {user_email}"
    body = f"""Message Content:<br><br>{content}<br><br>"""

    # 创建子进程并运行邮件发送函数
    process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
    process.start()

    return jsonify({'status': 'success', 'message': 'Email is being sent in the background'})


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

        return jsonify({'status': 'success', 'message': 'Issue broadcast is being sent in the background.', 'issue_id': issue_id})
    else:
        return jsonify({'status': 'failed', 'message': 'Failed to fetch issue information.', 'issue_id': issue_id}), 404


@app.route('/send_email/broadcast_pending', methods=['POST'])
def broadcast_pending_email():
    """
    Broadcast an email to notify all administrators that there is a pending booking.

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
        Dear Administrator,<br><br>

        This is a pending booking request waiting to be disposed. Below are booking details:<br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br><br>

        Please head to the room in time. Thank you.
        """

        # Create a new process to run the email broadcasting asynchronously
        process = Process(target=async_broadcast_email_to_all_administrators, args=(subject, body))
        process.start()

        return jsonify({'status': 'success', 'message': 'Reminder email is being sent in the background!', 'booking_id': booking_id})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.', 'booking_id': booking_id}), 404


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


if __name__ == '__main__':
    app.run(debug=True)

