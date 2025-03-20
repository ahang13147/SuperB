from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import random
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Flask 应用配置
app.secret_key = 'your_secret_key'  # 用于会话管理
app.config.update({
    'MAIL_SERVER': 'smtp.qq.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,       # 使用 TLS 加密
    'MAIL_USE_SSL': False,      # 不使用 SSL
    'MAIL_USERNAME': '2530681892@qq.com',
    'MAIL_PASSWORD': 'gnpunomuoqwhechd',
    'MAIL_DEFAULT_SENDER': ('Classroom System', '2530681892@qq.com')
})


mail = Mail(app)
verification_codes = {}  # 用于存储各邮箱的验证码及发送时间
code_expiry = 300  # 验证码有效时间，单位为秒（5 分钟）


@app.route('/')
def index():
    """渲染验证页面模板（可选）"""
    return render_template('login.html')


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
    接收 JSON 格式的请求数据，包含邮箱和验证码，验证是否正确且在有效期内。

    请求示例（JSON）:
    {
        "email": "your_email@dundee.ac.uk",
        "code": "123456"
    }

    返回示例（JSON）:
    成功:
    {
        "status": "success",
        "message": "Welcome, your_email@dundee.ac.uk!"
    }
    失败:
    {
        "status": "failed",
        "message": "错误信息..."
    }
    """
    data = request.get_json()
    if not data or 'email' not in data or 'code' not in data:
        return jsonify({'status': 'failed', 'message': 'Missing email or code parameter'}), 400

    email = data.get('email')
    code = data.get('code')

    try:
        entered_code = int(code)
    except ValueError:
        return jsonify({'status': 'failed', 'message': 'Invalid code format'}), 400

    if email not in verification_codes:
        return jsonify({'status': 'failed', 'message': 'Invalid email address'}), 400

    stored_code = verification_codes[email]['code']
    timestamp = verification_codes[email]['timestamp']

    # 检查验证码是否超时
    if time.time() - timestamp > code_expiry:
        del verification_codes[email]
        return jsonify(
            {'status': 'failed', 'message': 'The verification code has expired, please request a new one'}), 400

    if entered_code == stored_code:
        del verification_codes[email]
        return jsonify({'status': 'success', 'message': f'Welcome, {email}!'})
    else:
        return jsonify({'status': 'failed', 'message': 'Incorrect verification code, please try again'}), 400


if __name__ == '__main__':
    app.run(debug=True)
