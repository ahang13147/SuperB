# -*- coding: utf-8 -*-
"""
Author: Zibang Nie
Description: This Flask application sends reminder emails to users about their room bookings.
             It retrieves booking details from the database and sends an email to the user.
             The email includes booking details such as room name, location, start time, and end time.
             Each endpoint is responsible for sending a specific type of email based on the booking status.
             The response to each request is a JSON object containing the status of the email operation.

"""

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
import mysql.connector
from datetime import datetime, timedelta

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
        tuple: A tuple containing booking details (booking_id, user_email, room_name, room_location, start_time, end_time).
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


@app.route('/send_email/success', methods=['POST'])
def send_success_email():
    """
    Send an email notifying the user that their booking was successful.

    Request Format:
        POST method with 'booking_id' in form data (int).

    Response Format:
        JSON with 'status' and 'message'.
        'status' can be 'success' or 'failed'.
    """
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # Email content
        subject = f"Booking Successful: Room {room_name}"
        body = f"""
        Dear {user_email},

        Congratulations! Your room booking has been successfully confirmed. Below are your booking details:

        Booking ID: {booking_id}
        Room Name: {room_name}
        Room Location: {room_location}
        Start Time: {start_time}
        End Time: {end_time}

        Thank you for using our system, and we hope you enjoy your booking!
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking successful email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


@app.route('/send_email/rejected', methods=['POST'])
def send_rejected_email():
    """
    Send an email notifying the user that their booking was rejected by the administrator.

    Request Format:
        POST method with 'booking_id' in form data (int).

    Response Format:
        JSON with 'status' and 'message'.
        'status' can be 'success' or 'failed'.
    """
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # Email content
        subject = f"Booking Rejected: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking request has been rejected by the administrator. Below are your booking details:

        Booking ID: {booking_id}
        Room Name: {room_name}
        Room Location: {room_location}
        Booking Time: {start_time} - {end_time}

        Please contact the administrator for further clarification.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking rejected email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


@app.route('/send_email/cancelled', methods=['POST'])
def send_cancelled_email():
    """
    Send an email notifying the user that their booking has been cancelled.

    Request Format:
        POST method with 'booking_id' in form data (int).

    Response Format:
        JSON with 'status' and 'message'.
        'status' can be 'success' or 'failed'.
    """
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # Email content
        subject = f"Booking Cancelled: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking has been cancelled. Below are your booking details:

        Booking ID: {booking_id}
        Room Name: {room_name}
        Room Location: {room_location}
        Booking Time: {start_time} - {end_time}

        Thank you for your understanding.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking cancelled email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


@app.route('/send_email/failed', methods=['POST'])
def send_failed_email():
    """
    Send an email notifying the user that their booking failed.

    Request Format:
        POST method with 'booking_id' in form data (int).

    Response Format:
        JSON with 'status' and 'message'.
        'status' can be 'success' or 'failed'.
    """
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # Email content
        subject = f"Booking Failed: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking has failed. Below are your booking details:

        Booking ID: {booking_id}
        Room Name: {room_name}
        Room Location: {room_location}
        Booking Time: {start_time} - {end_time}

        Please check your booking details or contact the administrator for further assistance.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking failed email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


@app.route('/send_email/remind', methods=['POST'])
def send_remind_email():
    """
    Send a reminder email notifying the user that their booking is about to begin.

    Request Format:
        POST method with 'booking_id' in form data (int).

    Response Format:
        JSON with 'status' and 'message'.
        'status' can be 'success' or 'failed'.
    """
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        # Email content
        subject = f"Reminder: Your Booking for Room {room_name} is Approaching"
        body = f"""
        Dear {user_email},

        This is a reminder that your room booking is about to begin. Below are your booking details:

        Booking ID: {booking_id}
        Room Name: {room_name}
        Room Location: {room_location}
        Start Time: {start_time}
        End Time: {end_time}

        Please head to the room in time. Thank you.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


@app.route('/')
def index():
    """Render the main page"""
    return render_template('total_email.html')


if __name__ == '__main__':
    app.run(debug=True)
