import msal
import requests
import urllib.parse

# 直接硬编码 Azure 应用的配置
client_id = 'f40296ef-9aca-48b4-9ca1-b02e6d690f7c'  # 应用注册时获得的客户端ID
client_secret = 'JUV8Q~s~0D45yzMMLJmZuOT0hO53hwb84xHrebb~'  # 应用注册时获得的客户端密钥值
tenant_id = '52ff27b4-1ebf-4510-a74f-8940dbf42624'  # 租户ID
redirect_uri = 'https://101.200.197.132:8000/auth_callback'  # 设置为与Azure应用注册中的重定向URI相同

# 对 client_secret 进行 URL 编码
encoded_client_secret = urllib.parse.quote(client_secret)

# 1. 获取授权URL，用户通过浏览器访问并登录
authority = f'https://login.microsoftonline.com/{tenant_id}'
scopes = ['User.Read', 'Calendars.ReadWrite']

# 创建 ConfidentialClientApplication，而不是 PublicClientApplication
app = msal.ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)

# 获取授权码URL
auth_url = app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)
print(f'请访问以下URL登录并授权应用：\n{auth_url}')

# 2. 用户登录后，输入获取的授权码
auth_code = input("输入授权码：")

# 3. 使用授权码交换访问令牌
result = app.acquire_token_by_authorization_code(auth_code, redirect_uri=redirect_uri, scopes=scopes)

if 'access_token' in result:
    access_token = result['access_token']
    print("成功获取访问令牌!")
else:
    print(f"获取令牌失败: {result.get('error_description')}")
    exit()

# 4. 使用访问令牌访问 Graph API 创建事件
event_data = {
    "subject": "Client Meeting",
    "start": {
        "dateTime": "2025-03-14T15:00:00",
        "timeZone": "UTC"
    },
    "end": {
        "dateTime": "2025-03-14T15:30:00",
        "timeZone": "UTC"
    },
    "location": {
        "displayName": "Teams"
    },
    "attendees": [
        {
            "emailAddress": {
                "address": "2542881@dundee.ac.uk",
                "name": "Client"
            },
            "type": "required"
        }
    ],
}

graph_api_url = 'https://graph.microsoft.com/v1.0/me/events'
headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}

response = requests.post(graph_api_url, json=event_data, headers=headers)

if response.status_code == 201:
    print("事件已成功创建！")
else:
    print(f"创建事件失败: {response.status_code} - {response.text}")
