from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
import random
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuration for Flask application
app.secret_key = 'your_secret_key'  # Secret key for session management
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',  # Mail server (QQ Mail in this case)
    'MAIL_PORT': 465,  # SMTP server port (SSL)
    'MAIL_USE_SSL': True,  # Enable SSL for secure email sending
    'MAIL_USERNAME': '2530681892@qq.com',  # Your QQ email username
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',  # Your QQ email app password
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')  # Default sender for the emails
})

mail = Mail(app)
verification_codes = {}  # Dictionary to store verification codes for each email
code_expiry = 300  # Code expiry time (5 minutes)


@app.route('/')
def index():
    """Render the login page template."""
    return render_template('login.html')  # The template for login page


@app.route('/send_verification', methods=['POST'])
def send_verification():
    """
    Sends a verification code to the user's email.

    Request:
        - email (string): The email address of the user.

    Response:
        - Success: Sends a verification code to the provided email.
        - Failure: Returns a message if the email is not from '@dundee.ac.uk' or if sending the email fails.
    """
    email = request.form['email']  # Get the email address from the form data

    # Check if the email domain is '@dundee.ac.uk'
    if not email.endswith('@dundee.ac.uk'):
        flash("The email must be from the dundee.ac.uk domain", 'error')
        return redirect(url_for('index'))  # Redirect to the login page if email domain is incorrect

    # Generate a random 6-digit verification code
    verification_code = random.randint(100000, 999999)

    # Store the verification code and the timestamp for the email in the dictionary
    verification_codes[email] = {
        'code': verification_code,
        'timestamp': time.time()
    }

    try:
        # Create the email message
        msg = Message('Verification Code - Classroom System Login', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        msg.html = f'<p>Your verification code is: <strong>{verification_code}</strong></p>'

        # Send the email with the verification code
        mail.send(msg)
        flash('The verification code has been sent to your email, please check.', 'success')

    except Exception as e:
        flash(f"Failed to send email: {str(e)}", 'error')  # If email sending fails, show an error message

    return redirect(url_for('verify'))  # Redirect to the verify page where the user can enter the code


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """
    Verifies the user's entered verification code.

    Request (POST):
        - email (string): The email address of the user.
        - code (int): The verification code entered by the user.

    Response (JSON):
        - Success: If the code is correct, returns `status: success` with a welcome message.
        - Failed: If the email is invalid, or the code is incorrect/expired, returns `status: failed` with an error message.
    """
    if request.method == 'POST':
        email = request.form['email']  # Get the email from the form
        entered_code = int(request.form['code'])  # Get the entered code from the form

        # Check if the email exists in the verification_codes dictionary
        if email not in verification_codes:
            return jsonify({'status': 'failed', 'message': 'Invalid email address'})  # Invalid email

        # Retrieve the stored verification code and timestamp for the email
        stored_code = verification_codes[email]['code']
        timestamp = verification_codes[email]['timestamp']

        # Check if the verification code has expired
        if time.time() - timestamp > code_expiry:
            del verification_codes[email]  # Remove expired code from the dictionary
            return jsonify({'status': 'failed',
                            'message': 'The verification code has expired, please request a new one'})  # Expired code

        # Check if the entered code matches the stored code
        if entered_code == stored_code:
            del verification_codes[email]  # Remove the valid code from the dictionary after successful verification
            return jsonify({'status': 'success', 'message': f'Welcome, {email}!'})  # Successful verification

        else:
            return jsonify(
                {'status': 'failed', 'message': 'Incorrect verification code, please try again'})  # Incorrect code

    return render_template('verify.html')  # Render the verification page if the request method is GET


if __name__ == '__main__':
    app.run(debug=True)
