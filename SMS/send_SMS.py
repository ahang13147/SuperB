# -*- coding: utf-8 -*-
"""
Author: Your Name
Description: This Python script uses the Aliyun SMS API to send a verification code to a specified phone number.
             It creates an AcsClient using your AccessKey ID and AccessKey Secret, sends an SMS using a predefined template,
             and prints the response from the Aliyun server.

Usage:
    1. Replace 'PhoneNumbers', 'SignName', and 'TemplateCode' with desired phone number, SMS sign name, and template code.
    2. Run the script to send an SMS and view the response.

Dependencies:
    - Install the Aliyun Python SDK: `pip install aliyun-python-sdk-core`
"""

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json


# Create a client instance using AccessKey ID and AccessKey Secret
def create_client():
    access_key_id = ''  # Replace with your AccessKey ID
    access_key_secret = ''  # Replace with your AccessKey Secret

    # Create the AcsClient instance with the provided AccessKey and Secret
    client = AcsClient(access_key_id, access_key_secret, "cn-hangzhou")
    return client


def main():
    # Initialize the request client
    client = create_client()

    # Create a request to send the SMS
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')  # SMS API endpoint
    request.set_version('2017-05-25')  # API version
    request.set_action_name('SendSms')  # Action name for sending SMS

    # Set the parameters for the SMS request
    request.add_query_param('PhoneNumbers', '17375819888')  # Replace with the target phone number
    request.add_query_param('SignName', '邓迪教室预约')  # SMS sign name (must be approved by Aliyun)
    request.add_query_param('TemplateCode', 'SMS_480790042')  # SMS template code (must be created in Aliyun console)
    request.add_query_param('TemplateParam', json.dumps({"code": "111111"}))  # The verification code to send (JSON formatted)

    # Send the request and get the response
    response = client.do_action_with_exception(request)

    # Print the response from the Aliyun API
    print(json.loads(response))


if __name__ == '__main__':
    main()
