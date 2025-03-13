import msal
import requests

# Azure 应用注册信息
CLIENT_ID = 'a062851f-35e7-4b1d-aeb4-bd0e3f3726fa'
CLIENT_SECRET = 'k-z8Q~DWi8SOR2m..XcdM6Yjy8HFbiIwHLXX1bXC'
TENANT_ID = '52ff27b4-1ebf-4510-a74f-8940dbf42624'
SCOPES = ['https://graph.microsoft.com/.default']

# 获取OAuth2令牌
def get_access_token():
    authority = f'https://login.microsoftonline.com/{TENANT_ID}'
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET
    )

    result = app.acquire_token_for_client(scopes=SCOPES)

    if 'access_token' in result:
        return result['access_token']
    else:
        print('Error getting token:', result.get('error_description'))
        return None

def get_user_by_email(access_token, user_email):
    # 使用 '/users/{userEmail}' 端点获取用户信息
    url = f'https://graph.microsoft.com/v1.0/users/{user_email}'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        print(f"User ID: {user_info['id']}")  # 提取userId
        print(f"User Info: {user_info}")
    else:
        print(f"Error getting user info: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    access_token = get_access_token()

    if access_token:
        # 使用用户的电子邮件查询用户 ID
        user_email = '2542881@dundee.ac.uk'  # 替换为目标用户的电子邮件
        get_user_by_email(access_token, user_email)
