import msal
import requests
from datetime import datetime
import json
import webbrowser

# Microsoft Graph API 配置
CLIENT_ID = 'a062851f-35e7-4b1d-aeb4-bd0e3f3726fa'
CLIENT_SECRET = 'k-z8Q~DWi8SOR2m..XcdM6Yjy8HFbiIwHLXX1bXC'
TENANT_ID = '52ff27b4-1ebf-4510-a74f-8940dbf42624'
SCOPES = ['Calendars.ReadWrite']

# 认证 URL
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'


# 获取 Microsoft Graph API 访问令牌（委托权限）
def get_access_token():
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY
    )

    # 获取授权 URL，用户授权后重定向到回调 URL
    auth_url = app.get_authorization_request_url(SCOPES)
    print("Please go to the following URL and log in:", auth_url)

    # 打开浏览器让用户登录
    webbrowser.open(auth_url)

    # 用户登录并授权后，微软会重定向到回调 URL，包含授权码
    auth_code = input("Enter the authorization code here: ")

    # 使用授权码换取访问令牌
    result = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPES, redirect_uri="http://localhost")

    if "access_token" in result:
        return result["access_token"]
    else:
        print("Error obtaining access token")
        print(result)
        return None


# 使用 Microsoft Graph API 创建事件
def create_event(subject, start_time, end_time, location, attendees):
    access_token = get_access_token()

    if access_token:
        url = 'https://graph.microsoft.com/v1.0/me/events'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        event_data = {
            "subject": subject,
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            },
            "location": {
                "displayName": location
            },
            "attendees": [{"emailAddress": {"address": attendee}, "type": "required"} for attendee in attendees],
            "isOnlineMeeting": False
        }

        response = requests.post(url, headers=headers, data=json.dumps(event_data))

        if response.status_code == 201:
            print("Event created successfully!")
        else:
            print("Error creating event:", response.status_code, response.text)


if __name__ == '__main__':
    # 事件参数
    subject = "Team Meeting"
    start_time = "2025-03-13T10:00:00"  # 必须是 UTC 时间格式
    end_time = "2025-03-13T11:00:00"
    location = "Microsoft Teams"
    attendees = ["example@domain.com"]

    create_event(subject, start_time, end_time, location, attendees)
