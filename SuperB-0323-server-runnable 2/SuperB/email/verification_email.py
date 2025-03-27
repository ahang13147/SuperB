# Open testing page from http://127.0.0.1:5000,don't open verification_email.html page in browser directly

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import random
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',
    'MAIL_PORT': 465,
    'MAIL_USE_SSL': True,
    'MAIL_USERNAME': '2530681892@qq.com',
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')
})

mail = Mail(app)
verification_codes = {}
code_expiry = 300  # 5 minutes

@app.route('/')
def index():
    return render_template('login.html')  # Render the login page template

@app.route('/send_verification', methods=['POST'])
def send_verification():
    email = request.form['email']

    if not email.endswith('@dundee.ac.uk'):
        flash("The email must be from the dundee.ac.uk domain", 'error')
        return redirect(url_for('index'))

    verification_code = random.randint(100000, 999999)
    verification_codes[email] = {
        'code': verification_code,
        'timestamp': time.time()
    }

    try:
        msg = Message('Verification Code - Classroom System Login', recipients=[email])
        msg.body = f'Your verification code is: {verification_code}'
        msg.html = f'<p>Your verification code is: <strong>{verification_code}</strong></p>'
        mail.send(msg)
        flash('The verification code has been sent to your email, please check.', 'success')

    except Exception as e:
        flash(f"Failed to send email: {str(e)}", 'error')

    return redirect(url_for('verify'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        email = request.form['email']
        entered_code = int(request.form['code'])

        if email not in verification_codes:
            flash("Invalid email address", 'error')
            return redirect(url_for('index'))

        stored_code = verification_codes[email]['code']
        timestamp = verification_codes[email]['timestamp']

        if time.time() - timestamp > code_expiry:
            del verification_codes[email]
            flash("The verification code has expired, please request a new one", 'error')
            return redirect(url_for('index'))

        if entered_code == stored_code:
            del verification_codes[email]
            flash(f'Welcome, {email}!', 'success')
            return redirect(url_for('index'))

        else:
            flash("Incorrect verification code, please try again", 'error')
            return redirect(url_for('verify'))

    return render_template('verify.html')

if __name__ == '__main__':
    app.run(debug=True)
