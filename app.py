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
# Set session persistence
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=3)  # Set session duration to 3 hours
CORS(app, supports_credentials=True, origins=["https://www.diicsu.top:8000"])  # Allow access from all sources
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
#     "password": "root",
#     "database": "booking_system_db"
# }
#
# def get_db_connection():
#     return mysql.connector.connect(**db_config)

# --------------------------email-config--------------------------

# app.config.update({
#     'MAIL_SERVER': 'smtp.qq.com',
#     'MAIL_PORT': 587,
#     'MAIL_USE_TLS': True,
#     'MAIL_USE_SSL': False,
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

app.config['UPLOAD_FOLDER'] = 'static/uploads/avatars'  # The actual storage path
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # The limit is 2MB


# -------------------------profile-photo-----------------------

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    user_id = get_user_id_by_email()
    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    filename = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)

    file.save(save_path)

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({'error': 'User database record not found'}), 404

    user.avatar_path = os.path.join('avatars', unique_name)
    db.session.commit()

    # generate URL
    avatar_url = url_for('static', filename=f"uploads/{user.avatar_path}", _external=True)

    return jsonify({'url': avatar_url})


# Whitelist of allowed file types
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --------------------------email---------------------------

mail = Mail(app)
verification_codes = {}  # It is used to store the verification code of each email address and the time it was sent
code_expiry = 300  # The verification code is valid in seconds (5 minutes)


@app.route('/send_verification', methods=['POST'])
def send_verification():
    """
    Receive the request data in JSON format, including the email address, and generate and send a verification code to the email address.
    Require mailboxes to end with "@dundee.ac.uk".

    Sample request (JSON):
    {
        "email": "your_email@dundee.ac.uk"
    }

    Sample response (JSON):
    Succeed:
    {
        "status": "success",
        "message": "Verification code sent. Check your email.",
        "email": "your_email@dundee.ac.uk"
    }
    Fail:
    {
        "status": "failed",
        "message": "Error message...",
        "email": "your_email@dundee.ac.uk" or null
    }
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({
            'status': 'failed',
            'message': 'Missing email parameter',
            'email': None
        }), 400

    email = data.get('email')

    if not email.endswith('@dundee.ac.uk'):
        return jsonify({
            'status': 'failed',
            'message': 'The email must be from the dundee.ac.uk domain',
            'email': email
        }), 400

    # Generate a random 6-digit verification code
    verification_code = random.randint(100000, 999999)

    verification_codes[email] = {
        'code': verification_code,
        'timestamp': time.time()
    }

    try:

        subject = "Verification Code - Classroom System Login"
        body = f"""
        <p>Your verification code is: <strong>{verification_code}</strong></p>
        """
        send_email(email, subject, body)

        return jsonify({
            'status': 'success',
            'message': 'Verification code sent. Check your email.',
            'email': email
        })
    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': f'Failed to send email: {str(e)}',
            'email': email
        }), 500


@app.route('/verify', methods=['POST'])
def verify():
    """
    Verify the captcha and handle user redirects
    Request Format (JSON):
    {
        "email": "user@example.com",
        "code": "123456"
    }
    """
    data = request.get_json()

    if not data or 'email' not in data or 'code' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing required parameters'}), 400

    email = data['email'].lower().strip()
    code = data['code']

    try:
        entered_code = int(code)
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'Invalid code format'}), 400

    if email not in verification_codes:
        return jsonify({'status': 'failed', 'message': 'Invalid email address'}), 400

    stored_data = verification_codes[email]
    if time.time() - stored_data['timestamp'] > code_expiry:
        del verification_codes[email]
        return jsonify({'status': 'failed', 'message': 'Verification code expired'}), 400

    if entered_code != stored_data['code']:
        return jsonify({'status': 'failed', 'message': 'Incorrect verification code'}), 400

    del verification_codes[email]

    session.permanent = True
    session['user_email'] = email

    if is_user_blacklisted():
        return jsonify({
            'status': 'success',
            'redirect': url_for('black')
        })

    try:
        role_api_url = f"https://www.diicsu.top:8000/login_get_role?email={email}"
        role_response = requests.get(role_api_url, verify=False, timeout=5)

        if role_response.status_code == 200:
            role_data = role_response.json()
            user_role = role_data.get('role', 'user')
            session['user_role'] = user_role
        else:
            session['user_role'] = 'student'
    except Exception as e:
        app.logger.error(f"Role API error: {str(e)}")
        session['user_role'] = 'user'

        # Role-oriented jumps
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

    # Create a subprocess and run the mail sending function
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
# Each of the following interfaces takes the booking_id from the JSON request and includes the booking_id in the returned JSON
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


# todo : add send issue email and broadcast email (3.25)


def async_broadcast_email(subject, body):
    """
    Async version of broadcast_email, runs in a separate process.
    """
    with app.app_context():  # Ensure that there is a Flask context in the subprocess (for send_email, etc.)
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

        # Query the email addresses of all administrator users
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
    """Load the configuration file and return to the configuration dictionary"""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

db_config = config.get("db_config")


def get_db_connection():
    return mysql.connector.connect(**db_config)


# Get the Azure configuration
CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
AUTHORITY = config.get("AUTHORITY")
REDIRECT_URI = config.get("REDIRECT_URI")

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
    """Verify the time format HH:MM"""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False


def format_time(time_val):
    """
    Convert a time or timedelta object to a HH:MM format string
    If time_val is of type datetime.time, it is converted directly to a string
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
    """Generates a list of all dates from start_date to end_date inclusive"""
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT room_name FROM Rooms WHERE room_id = %s"
        cursor.execute(query, (room_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            return result['room_name']  # room_name
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

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        try:

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
            return None
    except Exception as e:
        print(f"Error fetching user info: {e}")
        return None


# Search user's ID
def get_user_id_by_email():
    user_email = session.get('user_email')
    if not user_email:
        return None  # If there is no user_email in the session, None is returned

    try:

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)
        try:

            cursor.execute("SELECT user_id FROM Users WHERE email = %s", (user_email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
        conn.close()

        if user:
            return user['user_id']
        else:
            return None
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None


# ---------------------------- login ----------------------------
@app.route('/')
def index():
    # todo
    session.permanent = True  # Force the session to be set to persistent
    return redirect(url_for('login'))


@app.route('/auth')
def auth():
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=REDIRECT_URI,
        prompt="select_account"
    )
    return redirect(auth_url)


@app.route('/auth_callback')
def auth_callback():
    # Handle Microsoft callbacks
    code = request.args.get('code')
    if not code:
        return "Authentication failed: The authorization code is missing", 400

    # Exchange the authorization code for the token
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
            return redirect(url_for('login'))  # If you are not logged in, you are redirected to the login page
        if is_user_blacklisted():
            return redirect(url_for('black'))
        return f(*args, **kwargs)

    return decorated_function


# def role_required(role):
#     def decorator(f):
#         @wraps(f)
#         def decorated_function(*args, **kwargs):
#             if 'user_role' not in session or session['user_role'] != role:
#                 return redirect(url_for('login'))
#             return f(*args, **kwargs)

#         return decorated_function

#     return decorator

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_role' not in session or session['user_role'] not in allowed_roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route('/booking_centre')
@login_required
@role_required(['professor', 'student', 'tutor'])
def booking_centre():
    return render_template('booking_centre.html')


@app.route('/my_reservation')
@login_required
@role_required(['professor', 'student', 'tutor'])
def my_reservation():
    return render_template('my_reservation.html')


@app.route('/user_profile')
@login_required
@role_required(['professor', 'student', 'tutor'])
def user_profile():
    return render_template('user_profile.html')


@app.route('/my_notification')
@login_required
@role_required(['professor', 'student', 'tutor'])
def my_notification():
    return render_template('my_notification.html')


@app.route('/error')
def error_page():
    return render_template('error.html')


@app.route('/contact')
@login_required
@role_required(['professor', 'student', 'tutor'])
def contact():
    return render_template('contact.html')


@app.route('/adminSidebar')
@login_required
# @role_required('admin')
@role_required(['admin'])
def adminSidebar():
    return render_template('adminSidebar.html')


@app.route('/Approval_Center')
@login_required
# @role_required('admin')
@role_required(['admin'])
def Approval_Center():
    return render_template('Approval_Center.html')


@app.route('/blacklist')
@login_required
# @role_required('admin')
@role_required(['admin'])
def blacklist():
    return render_template('blacklist.html')


@app.route('/booking_centre_admin')
@login_required
# @role_required('admin')
@role_required(['admin'])
def booking_centre_admin():
    return render_template('booking_centre_admin.html')


@app.route('/cancel_reservation')
@login_required
# @role_required('admin')
@role_required(['admin'])
def cancel_reservation():
    return render_template('cancel_reservation.html')


@app.route('/my_profile_admin')
@login_required
# @role_required('admin')
@role_required(['admin'])
def my_profile_admin():
    return render_template('my_profile_admin.html')


@app.route('/my_reservation_admin')
@login_required
# @role_required('admin')
@role_required(['admin'])
def my_reservation_admin():
    return render_template('my_reservation_admin.html')


@app.route('/notice_admin')
@login_required
# @role_required('admin')
@role_required(['admin'])
def notice_admin():
    return render_template('notice_admin.html')


@app.route('/room_management')
@login_required
# @role_required('admin')
@role_required(['admin'])
def room_management():
    return render_template('room_management.html')


@app.route('/user_management')
@login_required
# @role_required('admin')
@role_required(['admin'])
def user_management():
    return render_template('user_management.html')


@app.route('/usage_report_center.html')
@login_required
# @role_required('admin')
@role_required(['admin'])
def usage_report_center():
    return render_template('usage_report_center.html')


@app.route('/trust_list')
@login_required
# @role_required('admin')
@role_required(['admin'])
def trust_list():
    return render_template('trust_list.html')


@app.route('/room_issue_management')
@login_required
# @role_required('admin')
@role_required(['admin'])
def room_issue_management():
    return render_template('room_issue_management.html')


@app.route('/black')
# @login_required
def black():
    return render_template('black.html')


# Routing: Render login.html
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
    """Check that the user's mailbox is in the blacklist table"""
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

    # New: Check whether it is in the blacklist

    try:
        print(f"Calling role API with email: {user_email}")
        role_response = requests.get(
            f"https://www.diicsu.top:8000/login_get_role?email={user_email}",
            verify=False  # Ignore certificate validation
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT role FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()

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
#
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         if user_id:
#
#             cursor.execute("DELETE FROM Notifications WHERE user_id = %s", (user_id,))
#
#             cursor.execute("""
#                 DELETE FROM Approvals 
#                 WHERE booking_id IN (
#                     SELECT booking_id FROM Bookings WHERE user_id = %s
#                 )
#             """, (user_id,))
#
#             cursor.execute("DELETE FROM Bookings WHERE user_id = %s", (user_id,))
#
#             cursor.execute("DELETE FROM Approvals WHERE admin_id = %s", (user_id,))
#
#             cursor.execute("DELETE FROM Reports WHERE admin_id = %s", (user_id,))
#
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

    # Use the same database connection and transaction to delete user records directly and cascade deletion of related data
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if user_id:
            # Delete the user record directly, and all related data will be automatically deleted (via ON DELETE CASCADE)
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
        return jsonify({'error': 'No JSON data was received'}), 400

    room_id = data.get('room_id')
    action = data.get('action')

    if not room_id or not action:
        return jsonify({'error': 'The necessary parameters are missing'}), 400

    if action not in ['delete', 'restore']:
        return jsonify({'error': 'Invalid action type'}), 400

    new_status = 2 if action == 'delete' else 0

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        update_query = "UPDATE Rooms SET room_status = %s WHERE room_id = %s"
        cursor.execute(update_query, (new_status, room_id))
        conn.commit()
        return jsonify({
            'message': 'The room status is updated successfully',
            'room_id': room_id,
            'new_status': new_status
        })
    except Exception as e:
        return jsonify({'error': 'Failed to update room status', 'details': str(e)}), 500
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
        # Check if the record exists
        check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(check_query, (room_id, user_id))
        existing = cursor.fetchone()
        if not existing:
            return jsonify({"status": "error", "error": "Trusted user record not found"}), 404

        # Delete the record
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

        check_query = "SELECT * FROM Blacklist WHERE blacklist_id = %s"
        cursor.execute(check_query, (blacklist_id,))
        record = cursor.fetchone()
        if not record:
            return jsonify({"status": "error", "error": "Blacklist record not found"}), 404

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
    Example of request parameters:
    {
        "capacity": 20,
        "room_name": "conference room",
        "date": "2025-03-05",
        "start_time": "08:00",
        "end_time": "12:00",
        "equipment": "projector"
    }
    All parameters are optional and can be combined in any way
    """
    params = request.json or {}
    capacity = params.get('capacity')
    max_capacity = params.get('max_capacity')
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
        if max_capacity:
            query += " AND r.capacity <= %s"
            query_params.append(int(max_capacity))
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

        print("SQL:", query)
        print(":", query_params)

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
JOIN Users u ON b.user_id = u.user_id 


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

        # user_id = request.args.get('user_id')
        # todo: Add to get the current userID
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
                u.username,
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
            JOIN Users u ON b.user_id = u.user_id
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


@app.route('/finished-workflow-bookings', methods=['GET'])
def get_Finished_Workflow_bookings():
    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # todo : add user_id field
        # SQL query to get the scheduled record with status 'pending' and join the Users and Rooms tables
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


@app.route('/get-issues/<int:room_id>', methods=['GET'])
def get_issues_by_room(room_id):
    """
    Get the associated issue record via room_id (only issues and status are returned)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                issue,      
                status      
            FROM Issues
            WHERE room_id = %s
        """
        cursor.execute(query, (room_id,))
        issues = cursor.fetchall()

        return jsonify({
            "room_id": room_id,
            "count": len(issues),
            "issues": issues  # Each element contains only issues and statuses
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

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        user_id = get_user_id_by_email()

        # SQL query to connect the blacklist and Users tables to obtain the blacklist records and the corresponding usernames
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

        cursor.execute(query, (user_id,))
        blacklists = cursor.fetchall()

        for record in blacklists:
            record['start_date'] = record['start_date'].strftime("%Y-%m-%d")
            record['start_time'] = format_time(record['start_time'])
            record['end_date'] = record['end_date'].strftime("%Y-%m-%d")
            record['end_time'] = format_time(record['end_time'])

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

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL query to connect the blacklist and Users tables to obtain the blacklist records and the corresponding usernames
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

        cursor.execute(query)
        blacklists = cursor.fetchall()

        for record in blacklists:
            if record['added_date']:
                record['added_date'] = record['added_date'].strftime("%Y-%m-%d")
            if record['added_time']:
                record['added_time'] = format_time(record['added_time'])
            record['start_date'] = record['start_date'].strftime("%Y-%m-%d")
            record['start_time'] = format_time(record['start_time'])
            record['end_date'] = record['end_date'].strftime("%Y-%m-%d")
            record['end_time'] = format_time(record['end_time'])

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
        # Use dictionary=True to return results in dictionary format
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
        cursor = conn.cursor(dictionary=True)

        status = request.args.get('status')
        room_id = request.args.get('room_id')

        conditions = []
        params = []

        if status:
            conditions.append("i.status = %s")
            params.append(status)

        if room_id:

            if not room_id.isdigit():
                return jsonify({"error": "room_id must be a valid integer"}), 400
            conditions.append("i.room_id = %s")
            params.append(int(room_id))

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

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        base_query += " ORDER BY i.start_date DESC"

        cursor.execute(base_query, tuple(params))
        issues = cursor.fetchall()

        for issue in issues:

            for date_field in ['start_date', 'end_date']:
                if issue[date_field]:
                    issue[date_field] = issue[date_field].strftime("%Y-%m-%d")

            for time_field in ['start_time', 'end_time']:
                time_value = issue[time_field]
                if time_value:
                    if isinstance(time_value, timedelta):
                        # Convert timedelta to time string (HH:MM:SS)
                        total_seconds = int(time_value.total_seconds())
                        hours, remainder = divmod(total_seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        issue[time_field] = f"{hours:02}:{minutes:02}:{seconds:02}"
                    elif isinstance(time_value, str):
                        issue[time_field] = time_value
                    else:
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
        # 1. Get the current user's user_id through the session
        user_id = get_user_id_by_email()
        print(user_id)
        if not user_id:
            return jsonify({"error": "Not logged in or user not found"}), 401

        # 2. Query the user's notifications
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

        # 3. Return to the user's list of notifications
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
    Obtain the top 5 rooms within the specified time range
    Example of request parameters:
    {
        "start_date": "2025-03-01",
        "end_date": "2025-03-31"
    }
    """
    params = request.json or {}
    start_date = params.get('start_date')
    end_date = params.get('end_date')

    if not start_date or not end_date:
        return jsonify({"error": "Missing start_date or end_date parameter"}), 400

    try:

        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format (YYYY-MM-DD required)"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Corrected SQL (note parenthetical closure)
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

        # Processing results (converted to serializable format)
        for room in results:
            total_seconds = room['total_seconds'] or 0

            room['total_hours'] = round(total_seconds / 3600, 2)

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            room['total_duration'] = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            del room['total_seconds']

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

        # Query the current room data based on room_id
        cursor.execute("SELECT * FROM Rooms WHERE room_id = %s", (room_id,))
        existing_room = cursor.fetchone()
        if not existing_room:
            print(f"No room found with ID {room_id}.")
            return jsonify({"error": "Room not found"}), 404

        # Check that the submitted data is exactly the same as the existing data
        if (room_name == existing_room[1] and
                capacity == existing_room[2] and
                equipment == existing_room[3] and
                location == existing_room[4] and
                room_type == existing_room[5]):
            print("No changes detected.")
            return jsonify({"message": "No changes were made"}), 200

        # Check if the same room name already exists in other records (excludes the current record)
        cursor.execute("SELECT * FROM Rooms WHERE room_name = %s AND room_id != %s", (room_name, room_id))
        duplicate_room = cursor.fetchone()
        if duplicate_room:
            print(f"Room name '{room_name}' already exists.")
            return jsonify({"error": "Room name already exists"}), 400

        # Perform an update operation
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

        # Query and return updated room data
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

        # Check if the appointment exists and the status is pending
        cursor.execute(
            "SELECT * FROM Bookings WHERE booking_id = %s AND status = 'pending'",
            (booking_id,)
        )
        booking = cursor.fetchone()

        if not booking:
            print(f"No pending booking found with ID {booking_id}.")
            return jsonify({"error": "Booking not found or already processed"}), 404

        # Start a transaction
        # If the approval status is approved, additional conflict records and room status need to be updated
        if status == 'approved':
            # 1. Update the current appointment to approved
            cursor.execute(
                "UPDATE Bookings SET status = 'approved' WHERE booking_id = %s",
                (booking_id,)
            )

            # 2. Get the details of the current appointment (for future updates to other records)
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

            # 3. Update the records of other pending in the same room and in the same time period to failed
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
            # Query the booking_id of bookings that have been updated to failed (excluding the currently approved booking)
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

            failed_booking_ids = [row['booking_id'] for row in failed_rows] if failed_rows else []

            # 4. Update the Room_availability table to set the availability of the corresponding record to 2 (booked)
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
            # If the status is rejected, only the current appointment record is updated
            cursor.execute(
                "UPDATE Bookings SET status = 'rejected' WHERE booking_id = %s",
                (booking_id,)
            )
            # There is no need for failed_bookings-related logic
            failed_booking_ids = []  # Initialize to an empty list, as there is no failure involved in the rejected state

        conn.commit()

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

        # Gets the ID of the currently logged-in user
        current_user_id = get_user_id_by_email()

        # Gets the role of the currently logged-in user
        cursor.execute("SELECT role FROM Users WHERE user_id = %s", (current_user_id,))
        role_row = cursor.fetchone()
        current_user_role = role_row['role'] if role_row else None
        print(f"Current user_id = {current_user_id}, role = {current_user_role}")

        # Find appointments that you want to cancel (and haven't been canceled yet)
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

        # If the current user isn't an admin, they can only cancel their own Booking
        if current_user_role != 'admin':
            if booking['user_id'] != current_user_id:
                return jsonify({"error": "You are not allowed to cancel someone else's booking"}), 403

        # Update the booking to 'canceled' status
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

        # Re-obtain the updated appointment information
        cursor.execute("""
            SELECT booking_id, user_id, booking_date, status
            FROM Bookings
            WHERE booking_id = %s
        """, (booking_id,))
        updated_booking = cursor.fetchone()
        print(f"Updated booking: {updated_booking}")

        # If the current user is an administrator, the logic of "cancel 3 times" is not triggered, and success is returned
        if current_user_role == 'admin':
            return jsonify({
                "message": "Booking canceled by admin",
                "booking_id": updated_booking['booking_id'],
                "status": updated_booking['status']
            })

        # Here, it means that the ordinary user is canceling the reservation by himself
        user_id = updated_booking['user_id']
        booking_date = updated_booking['booking_date']

        # Count the number of cancellations made by the user on the same day
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

        # If the number of cancellations for the day is > = 3, the extra logic is executed
        if cancel_count >= 3:
            # Send a notification to the user
            cursor.execute("""
                INSERT INTO Notifications (user_id, message, notification_action, status)
                VALUES (%s, %s, 'alert', 'unread')
            """, (
                user_id,
                "You have canceled 3 bookings in one day. Please respect classroom resources."
            ))

            """
            subject = "Blacklisted due to multiple cancellations"
            body = "You have canceled 3 bookings in one day and have been blacklisted for 1 month."
            send_email_to_user(user_id, subject, body)
            """

            cursor.execute("""
                SELECT blacklist_id
                FROM Blacklist
                WHERE user_id = %s
                  AND end_date >= CURDATE()
            """, (user_id,))
            blacklisted = cursor.fetchone()

            if not blacklisted:
                # Not on the blacklist => Add it to the blacklist (ban for 1 month)
                admin_id = 1  # Here is an example of a dead admin ID, which you can find or define yourself
                reason = "Canceled 3 times in one day"

                now = datetime.now()
                end_date = now + timedelta(days=30)  # 1-month ban

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

                # Send a notification to all administrators
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

        query_select = "SELECT username, email, phone_number, role FROM Users WHERE user_id = %s"
        cursor.execute(query_select, (user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            return jsonify({"status": "error", "error": "User not found"}), 404

        # Check the difference between the updated field and the current data
        fields_to_update = {}
        for key, new_value in update_fields.items():
            if current_user[key] != new_value:
                fields_to_update[key] = new_value

        # If there is no actual change, the user information is not updated
        if not fields_to_update:
            return jsonify({"status": "success", "message": "No changes detected, data remains the same"}), 200

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

        cursor.execute("SELECT * FROM Issues WHERE issue_id = %s", (issue_id,))
        raw_issue = cursor.fetchone()

        if not raw_issue:
            conn.close()
            return jsonify({'error': 'Issue not found'}), 404

        # Convert tuples to dictionaries (fix field access issues)
        columns = [col[0] for col in cursor.description]
        issue = dict(zip(columns, raw_issue))

        # Prepare to update the fields
        update_fields = {
            'issue': data.get('issue', issue['issue']),
            'status': data.get('status', issue['status']),
            'start_date': data.get('start_date', issue['start_date']),
            'start_time': data.get('start_time', issue['start_time']),
            'end_date': issue['end_date'],
            'end_time': issue['end_time']
        }

        # Handling State Transitions (Fixed Date Calling Issue)
        if update_fields['status'] != issue['status']:
            if update_fields['status'] == 'resolved':
                # Use correctly imported date and datetime objects
                update_fields['end_date'] = date.today().strftime('%Y-%m-%d')
                update_fields['end_time'] = datetime.now().strftime('%H:%M:%S')
            elif issue['status'] == 'resolved' and update_fields['status'] != 'resolved':
                update_fields['end_date'] = None
                update_fields['end_time'] = None

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

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "error": str(err)}), 400
    finally:
        if conn:
            conn.close()


# todo: add check for the same insert
@app.route('/insert_booking_with_reason', methods=['POST'])
def insert_booking_with_reason():
    """The front-end enters reason and then calls this API for final insertion"""
    data = request.get_json()
    room_id = data.get('room_id')

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

        # Check if you already have the same booking record
        check_query = """
            SELECT * FROM Bookings 
            WHERE room_id = %s AND user_id = %s AND booking_date = %s 
            AND start_time = %s AND end_time = %s AND status IN ('approved', 'pending')
        """
        cursor.execute(check_query, (room_id, user_id, booking_date, start_time, end_time))
        existing_booking = cursor.fetchone()  # If there are identical records, the result is returned

        if existing_booking:
            return jsonify({"status": "error", "error": "Duplicate booking, the same booking already exists."}), 400

        # If there are no duplicates, insert the operation
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
    Inserts a new record into the Blacklist table.
    Sample request body (JSON):
    {
        "user_id": 2, # The target user to be added to the blacklist
        "start_date": "2025-03-20",
        "start_time": "09:00",
        "end_date": "2025-03-22",
        "end_time": "18:00",
        "reason": "Violation of rules"
    }
    Note: added_by will be automatically acquired by the currently logged-in user
    """
    try:
        data = request.json

        # The front-end passes in the ID of the user to be blacklisted
        user_id = data.get('user_id')
        # Gets the ID of the currently logged-in user as the added_by
        print("Session info at /insert-blacklist:", session)
        added_by = get_user_id_by_email()
        print("added_by:", added_by)
        start_date_str = data.get('start_date')
        start_time_str = data.get('start_time')
        end_date_str = data.get('end_date')
        end_time_str = data.get('end_time')
        reason = data.get('reason')

        if not all([user_id, added_by, start_date_str, start_time_str, end_date_str, end_time_str]):
            return jsonify({"error": "Missing required fields"}), 400

        # If the target user is the same as the current user, it is not allowed (prevent yourself from joining your own blacklist)
        if user_id == added_by:
            return jsonify({"error": "You cannot add yourself to the blacklist."}), 400

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

        # 1. Check whether the target user exists in the Users table
        cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
        target_user = cursor.fetchone()
        if not target_user:
            return jsonify({"error": "Target user does not exist"}), 400

        # 2. Check whether the target user is already on the blacklist
        check_query = "SELECT * FROM Blacklist WHERE user_id = %s"
        cursor.execute(check_query, (user_id,))
        existing_blacklist_entry = cursor.fetchall()

        if existing_blacklist_entry:
            return jsonify({"error": "User is already in the blacklist"}), 400

        # 3. Perform the insertion operation
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
    # If the frontend doesn't have a date and time passed in, consider automatically generating the current date and time
    added_date = data.get('added_date')  # The format should be 'YYYY-MM-DD'
    added_time = data.get('added_time')  # The format should be 'HH:MM:SS'
    notes = data.get('notes', '')

    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "error": "Database connection failed"}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS cnt FROM Users WHERE user_id = %s", (user_id,))
        user_count = cursor.fetchone()['cnt']
        if user_count == 0:
            return jsonify({"status": "error", "error": f"User with user_id={user_id} does not exist."}), 400

        cursor.execute("SELECT COUNT(*) AS cnt FROM Rooms WHERE room_id = %s", (room_id,))
        room_count = cursor.fetchone()['cnt']
        if room_count == 0:
            return jsonify({"status": "error", "error": f"Room with room_id={room_id} does not exist."}), 400

        check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
        cursor.execute(check_query, (room_id, user_id))
        existing = cursor.fetchone()
        if existing:
            return jsonify({
                "status": "error",
                "error": "The user is already in the trusted user list for this room."
            }), 400

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
#
#     added_date = data.get('added_date')
#     added_time = data.get('added_time')
#     notes = data.get('notes', '')

#     conn = get_db_connection()
#     if not conn:
#         return jsonify({"status": "error", "error": "Database connection failed"}), 500
#     try:
#
#         cursor = conn.cursor(dictionary=True)

#
#         check_query = "SELECT * FROM RoomTrustedUsers WHERE room_id = %s AND user_id = %s"
#         cursor.execute(check_query, (room_id, user_id))
#         existing = cursor.fetchone()
#         if existing:
#             return jsonify(
#                 {"status": "error", "error": "The user is already in the trusted user list for this room."}), 400

#
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

    app.run(
        host='0.0.0.0',
        port=8000,
        ssl_context=('diicsu.top.pem', 'diicsu.top.key')
    )

# if __name__ == '__main__':
#     print("\nRegistered routes:")
#     for rule in app.url_map.iter_rules():
#         print(f"→ {rule}")
#     app.run(host='0.0.0.0', port=8000, debug=True)
