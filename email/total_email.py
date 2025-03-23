from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS  # Import CORS
import mysql.connector
import urllib.parse
import pytz

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Configuration for Flask application
app.secret_key = 'your_secret_key'
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',  # Email server
    'MAIL_PORT': 587,  # Port (587 for TLS)
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': '2530681892@qq.com',  # Sender's email
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',  # Sender's email password
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
        tuple: A tuple containing booking details (booking_id, user_email, room_name, room_location, start_time, end_time, booking_date).
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
        SELECT b.booking_id, u.email, r.room_name, r.location, b.start_time, b.end_time, b.booking_date
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
            return booking_info  # Now returns (booking_id, user_email, room_name, room_location, start_time, end_time, booking_date)
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


# ============================
# Send Success Email
# ============================
@app.route('/send_email/success', methods=['POST'])
def send_success_email():
    """
    Send an email notifying the user that their booking was successful.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Successful: Room {room_name}"
        body = f"""
        Dear {user_email},

        Congratulations! Your room booking has been successfully confirmed. Below are your booking details:

        <br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br>

        Thank you for using our system, and we hope you enjoy your booking!
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking successful email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


# ============================
# Send Rejected Email
# ============================
@app.route('/send_email/rejected', methods=['POST'])
def send_rejected_email():
    """
    Send an email notifying the user that their booking was rejected by the administrator.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Rejected: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking request has been rejected by the administrator. Below are your booking details:

        <br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br>

        Please contact the administrator for further clarification.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking rejected email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


# ============================
# Send Cancelled Email
# ============================
@app.route('/send_email/cancelled', methods=['POST'])
def send_cancelled_email():
    """
    Send an email notifying the user that their booking has been cancelled.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Cancelled: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking has been cancelled. Below are your booking details:

        <br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br>

        Thank you for your understanding.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking cancelled email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


# ============================
# Send Failed Email
# ============================
@app.route('/send_email/failed', methods=['POST'])
def send_failed_email():
    """
    Send an email notifying the user that their booking failed.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Booking Failed: Room {room_name}"
        body = f"""
        Dear {user_email},

        We regret to inform you that your room booking has failed. Below are your booking details:

        <br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Booking Time:</strong> {start_time} - {end_time}<br>

        Please check your booking details or contact the administrator for further assistance.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Booking failed email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


# ============================
# Send Reminder Email
# ============================
@app.route('/send_email/remind', methods=['POST'])
def send_remind_email():
    """
    Send a reminder email notifying the user that their booking is about to begin.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)
    if booking_info:
        booking_id, user_email, room_name, room_location, start_time, end_time = booking_info

        subject = f"Reminder: Your Booking for Room {room_name} is Approaching"
        body = f"""
        Dear {user_email},

        This is a reminder that your room booking is about to begin. Below are your booking details:

        <br><br>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Room Name:</strong> {room_name}<br>
        <strong>Room Location:</strong> {room_location}<br>
        <strong>Start Time:</strong> {start_time}<br>
        <strong>End Time:</strong> {end_time}<br>

        Please head to the room in time. Thank you.
        """
        send_email(user_email, subject, body)
        return jsonify({'status': 'success', 'message': 'Reminder email sent!'})
    else:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})


# ============================
# Send Calendar Email
# ============================
import pytz
from datetime import datetime

@app.route('/send_email/calendar', methods=['POST'])
def send_calendar_email():
    """
    Send an email with a pre-filled Outlook calendar event link based on booking details.
    Request Format:
        POST method with 'booking_id' in JSON body (int).
    """
    data = request.get_json()
    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({'status': 'failed', 'message': 'Please provide a valid booking ID.'})

    booking_info = fetch_booking_info(booking_id)

    if not booking_info:
        return jsonify({'status': 'failed', 'message': 'No booking found for the provided ID.'})

    booking_id, user_email, room_name, room_location, start_time, end_time, booking_date = booking_info

    # Define time zones
    beijing_tz = pytz.timezone('Asia/Shanghai')  # Beijing Time zone (UTC+8)
    utc_tz = pytz.timezone('UTC')  # UTC time zone

    # Combine booking_date and start_time to create a datetime object
    start_datetime_str = f"{booking_date} {start_time}"
    end_datetime_str = f"{booking_date} {end_time}"

    # Convert start and end times from Beijing time to UTC time
    start_datetime_local = datetime.strptime(start_datetime_str, '%Y-%m-%d %H:%M:%S')
    end_datetime_local = datetime.strptime(end_datetime_str, '%Y-%m-%d %H:%M:%S')

    start_datetime_local = beijing_tz.localize(start_datetime_local)  # Localize to Beijing time
    end_datetime_local = beijing_tz.localize(end_datetime_local)  # Localize to Beijing time

    # Convert to UTC
    start_datetime_utc = start_datetime_local.astimezone(utc_tz)
    end_datetime_utc = end_datetime_local.astimezone(utc_tz)

    # Format to the required "YYYY-MM-DDTHH:MM:SSZ" format
    start_datetime = start_datetime_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_datetime = end_datetime_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

    summary = f"Booking for {room_name}"
    description = f"Room: {room_name}, Location: {room_location}, Start time: {start_time}, End time: {end_time}"
    location = room_location

    # Generate Outlook calendar link using times from the booking
    outlook_base_url = "https://outlook.office.com/calendar/0/deeplink/compose?"
    outlook_params = {
        "subject": summary,
        "startdt": start_datetime,  # Use the start time from the booking in the exact required format
        "enddt": end_datetime,  # Use the end time from the booking in the exact required format
        "body": description,
        "location": location
    }
    outlook_calendar_link = outlook_base_url + urllib.parse.urlencode(outlook_params)

    subject = f"Add Your Booking to Outlook Calendar: {room_name}"

    # Updated body_text to include HTML <a> tag for clickable hyperlink
    body_text = f"""Hi,

    Please use the following link to add your booking for room {room_name} to your Outlook calendar:
    <a href="{outlook_calendar_link}">Add to Outlook Calendar</a>

    Best regards,
    Your Team
    """

    message = Message(subject, recipients=[user_email])
    message.body = body_text  # Plain text version
    message.html = body_text  # HTML version for email clients that support it

    try:
        mail.send(message)
        return jsonify({'status': 'success', 'message': 'Calendar email sent successfully.'})
    except Exception as e:
        return jsonify({'status': 'failed', 'message': f"Error sending email: {e}"})


@app.route('/')
def index():
    """Render the main page"""
    return render_template('total_email.html')


if __name__ == '__main__':
    app.run(debug=True)
