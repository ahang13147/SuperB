import requests
import json

# 设置客户端ID和密钥
client_id = 'f40296ef-9aca-48b4-9ca1-b02e6d690f7c'  # 应用注册时获得的客户端ID
client_secret = 'JUV8Q~s~0D45yzMMLJmZuOT0hO53hwb84xHrebb~'  # 应用注册时获得的客户端密钥值
tenant_id = '52ff27b4-1ebf-4510-a74f-8940dbf42624'  # 租户ID

# 获取访问令牌
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret,
    'scope': 'https://graph.microsoft.com/.default'
}
response = requests.post(token_url, data=data)
access_token = response.json().get('access_token')
print(access_token)
user_id='8f622e36-3aba-4c62-bd7d-efd034e97550'
# 创建日历事件
event_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'
headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}
event_data = {
    "subject": "Meeting with team",
    "body": {
        "contentType": "HTML",
        "content": "Let's discuss the project updates."
    },
    "start": {
        "dateTime": "2025-03-21T10:00:00",
        "timeZone": "UTC"
    },
    "end": {
        "dateTime": "2025-03-22T11:00:00",
        "timeZone": "UTC"
    }
}
response = requests.post(event_url, headers=headers, data=json.dumps(event_data))
print("Status code:", response.status_code)
print("Headers:", response.headers)
print("Response text:", response.text)
if response.text:
    print(response.json())
else:
    print("No response content received.")

