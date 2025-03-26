# -*- coding: utf-8 -*-
"""
Author: Your Name
Description: This Python script uses the Aliyun SMS API to send a verification code to a specified phone number.
             It loops through a list of phone numbers, sending a verification code via Aliyun SMS API every 3 seconds.

Dependencies:
    pip install aliyun-python-sdk-core python-dotenv
"""

import os
import json
import time
from dotenv import load_dotenv
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


load_dotenv()


def create_client():
    access_key_id = os.getenv("ACCESS_KEY_ID")
    access_key_secret = os.getenv("ACCESS_KEY_SECRET")

    if not access_key_id or not access_key_secret:
        raise ValueError("请设置环境变量 ACCESS_KEY_ID 和 ACCESS_KEY_SECRET。")

    return AcsClient(access_key_id, access_key_secret, "cn-hangzhou")



def send_sms(phone_number: str, code: str):
    client = create_client()

    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('PhoneNumbers', phone_number)
    request.add_query_param('SignName', '邓迪教室预约')
    request.add_query_param('TemplateCode', 'SMS_480790042')
    request.add_query_param('TemplateParam', json.dumps({"code": code}))

    try:
        response = client.do_action_with_exception(request)
        print(f"[{phone_number}] 发送成功:", json.loads(response))
    except Exception as e:
        print(f"[{phone_number}] 发送失败:", str(e))


if __name__ == '__main__':
    phone_list = [
        "13508474328",
        "17375819888",
        "13943090540",
        "13142080514"
    ]

    code = "123456"


    while True:
        for phone in phone_list:
            send_sms(phone, code)
            time.sleep(3)
# -*- coding: utf-8 -*-
# """
# Author: Your Name
# Description: This script uses the Aliyun SMS API to send appointment reminder messages.
#              It loops through a list of users and sends SMS messages every 3 seconds, infinitely.
#
# Dependencies:
#     pip install aliyun-python-sdk-core python-dotenv
# """
#
# import os
# import json
# import time
# from dotenv import load_dotenv
# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.request import CommonRequest
#
#
# load_dotenv()
#
#
# def create_client():
#     access_key_id = os.getenv("ACCESS_KEY_ID")
#     access_key_secret = os.getenv("ACCESS_KEY_SECRET")
#
#     if not access_key_id or not access_key_secret:
#         raise ValueError("请设置环境变量 ACCESS_KEY_ID 和 ACCESS_KEY_SECRET。")
#
#     return AcsClient(access_key_id, access_key_secret, "cn-hangzhou")
#
#
#
# def send_sms(phone_number: str, room: str, start_time: str, end_time: str):
#     client = create_client()
#
#     request = CommonRequest()
#     request.set_accept_format('json')
#     request.set_domain('dysmsapi.aliyuncs.com')
#     request.set_version('2017-05-25')
#     request.set_action_name('SendSms')
#
#     request.add_query_param('PhoneNumbers', phone_number)
#     request.add_query_param('SignName', '邓迪教室预约')
#     request.add_query_param('TemplateCode', 'SMS_480965020')
#     request.add_query_param('TemplateParam', json.dumps({
#         "room": room,
#         "start_time": start_time,
#         "end_time": end_time
#     }))
#
#     try:
#         response = client.do_action_with_exception(request)
#         print(f"[{phone_number}] 发送成功:", json.loads(response))
#     except Exception as e:
#         print(f"[{phone_number}] 发送失败:", str(e))
#
#
#
# if __name__ == '__main__':
#
#     user_reservations = [
#         {"phone": "13508474328", "room": "101", "start": "09:00", "end": "10:00"},
#         {"phone": "17375819888", "room": "102", "start": "10:00", "end": "11:00"},
#         {"phone": "13943090540", "room": "103", "start": "11:00", "end": "12:00"},
#         {"phone": "13142080514", "room": "104", "start": "12:00", "end": "13:00"}
#     ]
#
#     print("开始无限循环发送预约提醒短信，每3秒发一条...")
#     while True:
#         for user in user_reservations:
#             send_sms(user["phone"], user["room"], user["start"], user["end"])
#             #time.sleep(3)


