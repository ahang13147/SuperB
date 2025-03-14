import msal
import requests
import webbrowser
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# 设置 Azure AD 应用的客户端 ID、客户端密钥和租户 ID
client_id = 'a062851f-35e7-4b1d-aeb4-bd0e3f3726fa'
client_secret = 'k-z8Q~DWi8SOR2m..XcdM6Yjy8HFbiIwHLXX1bXC'  # 使用 client_secret
tenant_id = '52ff27b4-1ebf-4510-a74f-8940dbf42624'
authority = f'https://login.microsoftonline.com/{tenant_id}'
redirect_uri = 'https://a342-202-197-66-71.ngrok-free.app'  # 使用ngrok暴露的URL作为回调地址

# 设置授权范围
scopes = ["User.Read", "Calendars.ReadWrite"]


# 本地服务器，用来捕获浏览器重定向的授权码
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Request received:", self.path)

        # 解析URL查询参数中的授权码
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        authorization_code = query_params.get('code', [None])[0]

        if authorization_code:
            print("Authorization code received:", authorization_code)
            global authorization_code_received
            authorization_code_received = authorization_code

            # 返回成功页面
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Authorization successful!</h1></body></html>")
        else:
            # 如果没有收到授权码，返回错误页面
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Error: Missing authorization code</h1></body></html>")


# 启动本地回调服务器
def start_local_server():
    global authorization_code_received
    authorization_code_received = None

    server = HTTPServer(('localhost', 8000), RequestHandler)
    print("Server started at http://localhost:8000, waiting for authorization code...")
    server.handle_request()

    return authorization_code_received


# 获取访问令牌
def get_access_token():
    # 创建 MSAL 应用，使用 ConfidentialClientApplication
    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority
    )

    # 去掉缓存令牌获取的部分，强制获取新的访问令牌
    # 尝试触发用户登录并获取授权码
    auth_url = app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)
    print("Opening browser for login...")
    webbrowser.open(auth_url)  # 打开浏览器让用户登录

    # 启动本地服务器以捕获授权码
    authorization_code = start_local_server()

    if not authorization_code:
        raise Exception("Failed to obtain authorization code.")

    # 使用授权码获取令牌
    try:
        token_result = app.acquire_token_by_authorization_code(
            authorization_code,
            scopes=scopes,
            redirect_uri=redirect_uri
        )
        print("Token result:", token_result)

        if "access_token" in token_result:
            return token_result["access_token"]
        else:
            print(f"Error while getting access token: {token_result.get('error')}")
            print(f"Error description: {token_result.get('error_description')}")
            raise Exception("Failed to obtain access token.")

    except Exception as e:
        print(f"Error during token acquisition: {e}")
        raise



def create_event(access_token):
    url = "https://graph.microsoft.com/v1.0/me/calendar/events"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    event_data = {
        "subject": "Let's go for lunch",
        "body": {
            "contentType": "HTML",
            "content": "Does mid month work for you?"
        },
        "start": {
            "dateTime": "2025-03-13T12:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "end": {
            "dateTime": "2025-03-13T14:00:00",
            "timeZone": "Pacific Standard Time"
        },
        "location": {
            "displayName": "Harry's Bar"
        },
        "attendees": [
            {
                "emailAddress": {
                    "address": "adelev@contoso.com",
                    "name": "Adele Vance"
                },
                "type": "required"
            }
        ]
    }

    # 调试输出 event_data
    # print("Event data:", json.dumps(event_data, indent=4))

    response = requests.post(url, headers=headers, json=event_data)

    print(f"Response status: {response.status_code}")
    print("Response text:", response.text)
    print("1")
    try:
        print("2")
        response_json = response.json()
        print("3")
        print("Response JSON:", json.dumps(response_json, indent=4))
        print("4")
    except json.JSONDecodeError:
        print("5")
        print("Error decoding JSON response:", response.text)

    if response.status_code == 201:
        print("Event created successfully!")
        print("Event ID:", response.json()["id"])
    else:
        print(f"Failed to create event: {response.status_code}")
        print(f"Response: {response.text}")
        raise Exception(f"Error: {response.status_code} - {response.text}")


# 主函数
if __name__ == "__main__":
    try:
        # 获取访问令牌
        access_token = get_access_token()
        print("Here!")
        print(access_token)
        # 创建日历事件
        create_event(access_token)

    except Exception as e:
        print(f"Error: {e}")