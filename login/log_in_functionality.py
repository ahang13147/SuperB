import msal
import requests
from flask import Flask, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 Flask 会话加密

# Azure AD 应用注册信息
CLIENT_ID = 'zyybvuyjip'  # 替换为你从 Azure 门户获取的 Client ID
CLIENT_SECRET = 'prH$TsWDu$wArlUv '  # 替换为你从 Azure 门户获取的 Client Secret
AUTHORITY = 'https://login.microsoftonline.com/common'
REDIRECT_URI = 'http://localhost:8000/getAToken'  # 替换为你的重定向 URI

# MSAL 客户端应用对象
msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
)


# 获取授权码 URL
def get_auth_url():
    return msal_app.get_authorization_request_url(
        scopes=["User.Read"],  # 请求用户数据权限
        redirect_uri=REDIRECT_URI
    )


@app.route('/')
def index():
    return redirect(get_auth_url())  # 重定向到 Microsoft 登录页面


@app.route('/getAToken')
def authorized():
    # 通过授权码换取访问令牌
    code = request.args.get('code')
    if not code:
        return 'No code found in response.'

    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read"],  # 请求用户数据权限
        redirect_uri=REDIRECT_URI
    )

    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('profile'))
    else:
        return f"Error: {result.get('error_description')}"


@app.route('/profile')
def profile():
    if 'access_token' not in session:
        return redirect(url_for('index'))

    # 使用 access token 获取用户信息
    access_token = session['access_token']
    headers = {'Authorization': f'Bearer {access_token}'}
    user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()

    return f'Hello, {user_info["displayName"]}!'


if __name__ == '__main__':
    app.run(port=8000)
