# Author: Zibang Nie, Guanhang Zhang
# This is a Flask application that implements a login system using email verification.
# The user enters their email, receives a verification code sent to their email address,
# and verifies the code within a specified time limit.
# The application uses Flask, Flask-Mail, and generates a 6-digit code.

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import random
import time

# Create a Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Configure the mail server (QQ email's SMTP server)
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',  # SMTP server for QQ email
    'MAIL_PORT': 465,  # Port 465 for SSL encryption
    'MAIL_USE_SSL': True,  # Use SSL encryption
    'MAIL_USERNAME': '2530681892@qq.com',  # Sender email address
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',  # Authorization code for the sender's email
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')  # Sender information (with name)
})

# Initialize the mail instance
mail = Mail(app)

# Dictionary to store verification codes and their timestamps
verification_codes = {}
code_expiry = 300  # Code expiry time in seconds (5 minutes)

# Route to the login page
@app.route('/')
def index():
    return render_template('login.html')  # Render the login page template

# Route to send the verification email
@app.route('/send_verification', methods=['POST'])
def send_verification():
    email = request.form['email']  # Get the email entered by the user
    print(f"Received user's email: {email}")  # Debugging message

    # Validate the email domain
    if not email.endswith('@dundee.ac.uk'):
        flash("The email must be from the dundee.ac.uk domain", 'error')
        return redirect(url_for('index'))

    # Generate a 6-digit verification code
    verification_code = random.randint(100000, 999999)
    verification_codes[email] = {
        'code': verification_code,
        'timestamp': time.time()  # Store the timestamp when the code was generated
    }

    print(f"Generated verification code: {verification_code}")  # Debugging message

    try:
        # Create the email content
        msg = Message('Verification Code - Classroom System Login',
                      recipients=[email])  # Recipient's email address

        # Set the email content in both plain text and HTML format
        msg.body = f'Your verification code is: {verification_code}'
        msg.html = f'<p>Your verification code is: <strong>{verification_code}</strong></p>'

        # Send the email
        print(f"Sending email to: {email}")  # Debugging message
        mail.send(msg)
        flash('The verification code has been sent to your email, please check.', 'success')

    except Exception as e:
        print(f"Failed to send email: {str(e)}")  # Print detailed error message
        flash(f"Failed to send email: {str(e)}", 'error')

    return redirect(url_for('verify'))  # Redirect to the verification page

# Route to verify the code entered by the user
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email = request.form['email']
        entered_code = int(request.form['code'])

        # Check if the email exists in the verification codes dictionary
        if email not in verification_codes:
            flash("Invalid email address", 'error')
            return redirect(url_for('index'))

        stored_code = verification_codes[email]['code']
        timestamp = verification_codes[email]['timestamp']

        # Check if the verification code has expired
        if time.time() - timestamp > code_expiry:
            del verification_codes[email]  # Delete the expired code
            flash("The verification code has expired, please request a new one", 'error')
            return redirect(url_for('index'))

        # Validate the entered code
        if entered_code == stored_code:
            del verification_codes[email]  # Delete the code after successful verification
            flash(f'Welcome, {email}!', 'success')
            return redirect(url_for('index'))  # Redirect to the login page

        else:
            flash("Incorrect verification code, please try again", 'error')
            return redirect(url_for('verify'))  # Redirect back to the verification page

    return render_template('verify.html')  # Render the verification input page

# Run the Flask application with debugging enabled
if __name__ == '__main__':
    app.run(debug=True)
