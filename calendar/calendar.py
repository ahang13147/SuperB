import asyncio
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.event import Event
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.date_time_time_zone import DateTimeTimeZone
from msgraph.generated.models.location import Location
from msgraph.generated.models.attendee import Attendee
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.attendee_type import AttendeeType
from kiota_abstractions.base_request_configuration import RequestConfiguration

# 应用注册信息
tenant_id = '52ff27b4-1ebf-4510-a74f-8940dbf42624'
client_id = 'f40296ef-9aca-48b4-9ca1-b02e6d690f7c'
client_secret = 'JUV8Q~s~0D45yzMMLJmZuOT0hO53hwb84xHrebb~'  # 替换为实际生成的 client_secret

# 使用 ClientSecretCredential 进行认证
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

# 初始化 GraphServiceClient（应用身份验证下不能使用 /me 端点）
graph_client = GraphServiceClient(credential)

# 创建一个事件
async def create_event():
    request_body = Event(
        subject="Let's go for lunch",
        body=ItemBody(
            content_type=BodyType.Html,
            content="Does noon work for you?"
        ),
        start=DateTimeTimeZone(
            date_time="2025-03-20T12:00:00",
            time_zone="Pacific Standard Time"
        ),
        end=DateTimeTimeZone(
            date_time="2025-03-20T14:00:00",
            time_zone="Pacific Standard Time"
        ),
        location=Location(
            display_name="Harry's Bar"
        ),
        attendees=[
            Attendee(
                email_address=EmailAddress(
                    address="2542881@dundee.ac.uk",
                    name="Samantha Booth"
                ),
                type=AttendeeType.Required
            ),
        ],
        allow_new_time_proposals=True,
        transaction_id="7E163156-7762-4BEB-A1C6-729EA81755A7"
    )

    request_configuration = RequestConfiguration()
    request_configuration.headers.add("Prefer", "outlook.timezone=\"Pacific Standard Time\"")

    try:
        # 使用 by_user_id 方法指定具体的用户ID（例如用户的邮箱地址）
        user_id = "2542881@dundee.ac.uk"  # 替换为实际的用户ID或邮箱地址
        result = await graph_client.users.by_user_id(user_id).events.post(request_body, request_configuration=request_configuration)
        print(f"Event created: {result}")
    except Exception as e:
        print(f"Error creating event: {e}")

# 运行异步函数
if __name__ == '__main__':
    asyncio.run(create_event())
