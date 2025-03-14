import msal

# 设置您的应用程序信息
client_id = 'a062851f-35e7-4b1d-aeb4-bd0e3f3726fa'
client_secret = 'k-z8Q~DWi8SOR2m..XcdM6Yjy8HFbiIwHLXX1bXC'  # 使用 client_secret
tenant_id = '52ff27b4-1ebf-4510-a74f-8940dbf42624'

# 设置 Azure AD 授权服务 URL
authority = f"https://login.microsoftonline.com/{tenant_id}"

# 创建 MSAL 应用对象
app = msal.ConfidentialClientApplication(client_id, client_credential=client_secret, authority=authority)

# 获取访问令牌
token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

# 检查是否成功获取令牌
if "access_token" in token_response:
    access_token = token_response["access_token"]
    print(access_token)
else:
    print("Failed to obtain access token")
    print(token_response)
