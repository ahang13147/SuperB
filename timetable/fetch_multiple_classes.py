import requests
from bs4 import BeautifulSoup
import json
import re
import time

"""
Description:
    This script retrieves the course schedules for all classes in all majors 
    at Central South University's Dundee International College (CSU).
    1. Initiates a session to maintain cookies.
    2. Iterates over all academic years (2022-2024).
    3. Retrieves the list of available majors for each year.
    4. Retrieves the list of available classes for each major.
    5. Fetches the schedule for each class.
    6. Parses and displays the schedule data.

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
session.get(url_main, headers=headers)

# Define academic years
academic_years = ["2022", "2023", "2024"]
xnxq01id = "2024-2025-2"  # Semester ID

url_zy = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
url_bj = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

for year in academic_years:
    print(f"\nFetching majors for year {year}...")

    # Select year and fetch majors
    data_zy = {"yxbh": "tc9qn3Xixg", "rxnf": year}
    response_zy = session.post(url_zy, data=data_zy, headers=headers)

    if response_zy.status_code != 200 or not response_zy.text.strip():
        print(f"⚠️ Warning: Failed to fetch majors for {year}, Status Code: {response_zy.status_code}")
        continue

    fixed_json_text = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_zy.text)
    fixed_json_text = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text)

    try:
        major_list = json.loads(fixed_json_text)
    except json.JSONDecodeError:
        print(f"⚠️ Warning: JSON parsing failed for majors in {year}. Response:\n{response_zy.text}")
        continue

    for major in major_list:
        major_id = major["jx01id"]
        major_name = major["zymc"]
        print(f"\nFetching classes for major: {major_name} ({year})...")

        # Fetch class list for the major
        data_bj = {"yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id, "xnxq01id": xnxq01id}
        response_bj = session.post(url_bj, data=data_bj, headers=headers)

        if response_bj.status_code != 200 or not response_bj.text.strip():
            print(f"⚠️ Warning: Failed to fetch classes for {major_name} ({year}), Status Code: {response_bj.status_code}")
            print(f"Response content: {response_bj.text}")  # Debugging info
            continue

        fixed_json_text_bj = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_bj.text)
        fixed_json_text_bj = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text_bj)

        try:
            class_list = json.loads(fixed_json_text_bj)
        except json.JSONDecodeError:
            print(f"⚠️ Warning: JSON parsing failed for classes in {major_name} ({year}). Response:\n{response_bj.text}")
            continue

        for class_info in class_list:
            class_id = class_info["xx04id"]
            class_name = class_info["bj"]
            print(f"Fetching schedule for class: {class_name} ({year})...")

            post_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
            form_data = {
                "type": "xx04",
                "isview": "1",
                "xx04id": class_id,
                "yxbh": "tc9qn3Xixg",
                "rxnf": year,
                "zy": major_id,
                "bjbh": class_name,
                "zc": "1",
                "xnxq01id": xnxq01id,
                "xx04mc": "",
                "sfFD": "1"
            }

            headers["Referer"] = url_main
            response_kb = session.post(post_url, data=form_data, headers=headers)

            if response_kb.status_code != 200 or not response_kb.text.strip():
                print(f"⚠️ Warning: Failed to fetch schedule for {class_name} ({year}), Status Code: {response_kb.status_code}")
                continue

            soup = BeautifulSoup(response_kb.text, "html.parser")
            table = soup.find("table")

            if table:
                print(f"\nSchedule for {class_name} ({year}):")
                rows = table.find_all("tr")
                for row in rows:
                    cols = row.find_all("td")
                    print([col.text.strip() for col in cols])
            else:
                print(f"⚠️ Warning: Schedule not found for {class_name} ({year})")

            time.sleep(2)  # Prevent excessive requests
