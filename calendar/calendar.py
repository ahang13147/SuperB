import msal
import requests
import datetime
import pytz  # 用于处理时区

# Azure 应用注册信息
CLIENT_ID = 'a062851f-35e7-4b1d-aeb4-bd0e3f3726fa'
CLIENT_SECRET = 'k-z8Q~DWi8SOR2m..XcdM6Yjy8HFbiIwHLXX1bXC'
TENANT_ID = '52ff27b4-1ebf-4510-a74f-8940dbf42624'
SCOPES = ['https://graph.microsoft.com/.default']  # 修改此行

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


# 创建活动
def create_event(access_token, user_id, start_time, end_time, location, description):
    url = f'https://graph.microsoft.com/v1.0/users/{user_id}/events'  # 修改此行，使用特定用户的 ID

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    event_data = {
        "subject": "Sample Event",  # 活动标题
        "body": {
            "contentType": "HTML",
            "content": description  # 活动描述
        },
        "start": {
            "dateTime": start_time,
            "timeZone": "UTC"  # 确保时区是UTC
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "UTC"  # 确保时区是UTC
        },
        "location": {
            "displayName": location  # 活动地点
        }
    }

    response = requests.post(url, headers=headers, json=event_data)

    if response.status_code == 201:
        print('Event created successfully!')
    else:
        print('Error creating event:', response.json())


# 主程序
if __name__ == '__main__':
    access_token = get_access_token()

    if access_token:
        # 设置活动的开始时间、结束时间、地点和描述
        tz = pytz.timezone('UTC')  # 设置时区为 UTC
        start_time = datetime.datetime(2025, 3, 15, 10, 0, 0, 0).replace(tzinfo=tz).isoformat()  # 格式化时间
        end_time = datetime.datetime(2025, 3, 15, 11, 0, 0, 0).replace(tzinfo=tz).isoformat()  # 格式化时间
        location = "Meeting Room A"
        description = "This is a detailed description of the event."

        # 使用特定用户的 user_id
        user_id = '2542881@dundee.ac.uk'  # 替换为实际的用户 ID 或邮箱地址

        create_event(access_token, user_id, start_time, end_time, location, description)
