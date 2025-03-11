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
REDIRECT_URI = 'https://9553-116-128-238-47.ngrok-free.app/getAToken'   # 必须与Azure门户注册的一致

# 初始化MSAL应用
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)


@app.route('/')
def index():
    # 如果已登录则跳转个人页，否则显示登录界面
    if 'access_token' in session:
        return redirect(url_for('profile'))
    return render_template('login.html')  # 渲染登录界面


@app.route('/login')
def login():
    # 生成Microsoft登录URL
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
    # 显示用户信息
    if 'access_token' not in session:
        return redirect(url_for('index'))

    headers = {'Authorization': f'Bearer {session["access_token"]}'}
    user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()

    return f'''
        <h1>欢迎回来，{user_info.get('displayName')}!</h1>
        <p>邮箱：{user_info.get('mail')}</p>
        <a href="/logout">退出登录</a>
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