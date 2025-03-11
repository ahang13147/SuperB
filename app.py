# this is for the login function, which need to be put at the top level of the whole project files
import msal
import requests
from flask import Flask, redirect, request, session, url_for, render_template

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key_here'

# Azure配置
CLIENT_ID = '736efa73-315a-4b77-a273-0447f5e2a27d'
CLIENT_SECRET = 'SmK8Q~kGj~gKhSU0ZFE.Z0VC~6NMMvQ8qdBm4atq'
AUTHORITY = 'https://login.microsoftonline.com/common'
REDIRECT_URI = 'https://9553-116-128-238-47.ngrok-free.app/getAToken'   # Must be consistent with Azure portal registration

# 初始化MSAL应用
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)


@app.route('/')
def index():
    # If you have logged in, the personal page is displayed. Otherwise, the login page is displayed
    if 'access_token' in session:
        return redirect(url_for('profile'))
    return render_template('login.html')


@app.route('/login')
def login():
    # Generate the Microsoft login URL
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read"],
        redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


@app.route('/getAToken')
def authorized():
    # 处理Microsoft回调
    code = request.args.get('code')
    if not code:
        return "Authentication failure: The authorization code is missing", 400

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
        return f"Authentication error：{result.get('error_description')}", 500


@app.route('/profile')
def profile():
    # 显示用户信息
    if 'access_token' not in session:
        return redirect(url_for('index'))

    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()

    return f'''
        <h1>welcome back，{user_info.get('displayName')}!</h1>
        <p>email：{user_info.get('mail')}</p>
        <a href="/logout">log out</a>
    '''


@app.route('/logout')
def logout():
    # 清除会话
    session.clear()
    # 跳转到Microsoft全局登出
    return redirect(
        "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        "?post_logout_redirect_uri=" + url_for('index', _external=True)
    )


if __name__ == '__main__':
    app.run(port=8000, debug=True)