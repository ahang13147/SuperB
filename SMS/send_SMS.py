# -*- coding: utf-8 -*-
"""
Author: Your Name
Description: This Python script uses the Aliyun SMS API to send a verification code to a specified phone number.
             It creates an AcsClient using AccessKey ID and AccessKey Secret obtained from environment variables,
             sends an SMS using a predefined template, and prints the response from the Aliyun server.

Usage:
    1. 设置环境变量 ACCESS_KEY_ID 和 ACCESS_KEY_SECRET 为您的阿里云 AccessKey ID 和 AccessKey Secret。
    2. 替换 'PhoneNumbers', 'SignName' 和 'TemplateCode' 为目标手机号、短信签名和模板代码。
    3. 运行脚本发送短信并查看响应。

Dependencies:
    - 安装阿里云 Python SDK: `pip install aliyun-python-sdk-core`
"""

import os
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


# 从环境变量中获取 AccessKey ID 和 AccessKey Secret
def create_client():
    access_key_id = os.getenv("ACCESS_KEY_ID")
    access_key_secret = os.getenv("ACCESS_KEY_SECRET")

    if not access_key_id or not access_key_secret:
        raise ValueError("请确保环境变量 ACCESS_KEY_ID 和 ACCESS_KEY_SECRET 已设置。")

    # 创建 AcsClient 实例
    client = AcsClient(access_key_id, access_key_secret, "cn-hangzhou")
    return client


def main():
    # 初始化请求客户端
    client = create_client()

    # 创建发送短信的请求
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')  # 短信 API 域名
    request.set_version('2017-05-25')  # API 版本
    request.set_action_name('SendSms')  # 发送短信的 API 操作名称

    # 设置短信请求参数
    request.add_query_param('PhoneNumbers', '17375819888')  # 目标手机号
    request.add_query_param('SignName', '邓迪教室预约')  # 短信签名（需阿里云审核通过）
    request.add_query_param('TemplateCode', 'SMS_480790042')  # 短信模板代码（需在阿里云控制台创建）
    request.add_query_param('TemplateParam', json.dumps({"code": "000000"}))  # 验证码（JSON 格式）

    # 发送请求并获取响应
    response = client.do_action_with_exception(request)
    print(json.loads(response))


if __name__ == '__main__':
    main()
