import requests
from bs4 import BeautifulSoup
import json
import re

"""
Description: 
    This script retrieves the course schedule for a specific class (Computer D2401) at Central South University 
    (CSU) by making HTTP requests to the university's academic system. It performs the following tasks:
    1. Initiates a session to maintain cookies.
    2. Retrieves the list of available majors and filters for Computer Science and Technology.
    3. Retrieves the list of available classes and filters for Computer D2401.
    4. Fetches the schedule for the selected class.
    5. Parses and displays the schedule data.

Author: Zibang Nie, Xin Yu, Siyan Guo
Version: 2025-03-04
"""

# Start session to maintain JSESSIONID
session = requests.Session()

# Get cookies
url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": url_main
}
response_main = session.get(url_main, headers=headers)
print("Cookies obtained:", session.cookies.get_dict())

# Select college
url_zy = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
data_zy = {
    "yxbh": "tc9qn3Xixg",  # Dundee International College
    "rxnf": ""
}
session.post(url_zy, data=data_zy, headers=headers)

# Query class (initialization)
url_bj_init = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"
data_bj_init = {"yxbh": "tc9qn3Xixg"}
session.post(url_bj_init, data=data_bj_init, headers=headers)

# Select grade
data_zy["rxnf"] = "2024"
session.post(url_zy, data=data_zy, headers=headers)

# Get major list
response_zy = session.post(url_zy, data=data_zy, headers=headers)
fixed_json_text = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_zy.text)
fixed_json_text = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text)

zy_list = json.loads(fixed_json_text)
zy_id = next((zy["jx01id"] for zy in zy_list if "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f" in zy["zymc"]), None)

if not zy_id:
    print("Computer Science and Technology major not found")
    exit()
print(f"Computer Science and Technology Major ID: {zy_id}")

# Select major
data_bj_zy = {
    "yxbh": "tc9qn3Xixg",
    "rxnf": "2024",
    "zy": zy_id
}
session.post(url_bj_init, data=data_bj_zy, headers=headers)

# Select class
data_bj_class = {
    "yxbh": "tc9qn3Xixg",
    "rxnf": "2024",
    "zy": zy_id,
    "xnxq01id": "2024-2025-2"
}
response_bj = session.post(url_bj_init, data=data_bj_class, headers=headers)
fixed_json_text_bj = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_bj.text)
fixed_json_text_bj = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text_bj)

bj_list = json.loads(fixed_json_text_bj)
bj_id = next((bj["xx04id"] for bj in bj_list if "\u8ba1\u7b97\u673aD2401" in bj["bj"]), None)

if not bj_id:
    print("Computer D2401 class not found")
    exit()
print(f"Computer D2401 Class ID: {bj_id}")

# Query schedule
post_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
form_data = {
    "type": "xx04",
    "isview": "1",
    "xx04id": bj_id,
    "yxbh": "tc9qn3Xixg",
    "rxnf": "2024",
    "zy": zy_id,
    "bjbh": "\u8ba1\u7b97\u673aD2401",
    "zc": "1",
    "xnxq01id": "2024-2025-2",
    "xx04mc": "",
    "sfFD": "1"
}

# Update Referer
headers["Referer"] = url_main
response_kb = session.post(post_url, data=form_data, headers=headers)

# Parse schedule
soup = BeautifulSoup(response_kb.text, "html.parser")
table = soup.find("table")

if table:
    print("Computer D2401 Week 1 Schedule:")
    rows = table.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        print([col.text.strip() for col in cols])
else:
    print("Schedule data not found")
