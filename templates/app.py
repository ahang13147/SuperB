import msal
import requests
from flask import Flask, redirect, request, session, url_for, render_template
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_ultra_secure_key_123!'  # 建议使用更复杂的密钥
CORS(app, resources={r"/*": {"origins": "http://localhost:8001"}}, supports_credentials=True)

# Azure配置
CLIENT_ID = '736efa73-315a-4b77-a273-0447f5e2a27d'
CLIENT_SECRET = 'SmK8Q~kGj~gKhSU0ZFE.Z0VC~6NMMvQ8qdBm4atq'
AUTHORITY = 'https://login.microsoftonline.com/common'
REDIRECT_URI = 'http://localhost:8000/auth_callback'

msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)


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
        redirect_uri=REDIRECT_URI
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


@app.route('/profile')
def profile():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()

    # 提取用户信息
    profile_data = {
        'name': user_info.get('displayName', '未知用户'),
        'email': user_info.get('mail', '无邮箱信息'),
        'id': user_info.get('id', ''),
        'job_title': user_info.get('jobTitle', '无职位信息'),
        'company_name': user_info.get('companyName', '无公司信息'),
        'phone_number': user_info.get('mobilePhone', '无电话号码'),
        'raw_data': user_info  # 传递完整原始数据
    }

    return render_template('user_profile.html', **profile_data)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)