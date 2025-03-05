import requests
from bs4 import BeautifulSoup
import json
import re
import time

"""
This script retrieves the classroom schedule for all classes at Central South University's 
Dundee International College (CSU). It extracts only the classroom names 
and consolidates them into a structured timetable format.

Author: Zibang Nie, Xin Yu, Siyan Guo
Version: 2025-03-04
"""

# ============================ Initialize Timetable ============================
# 7 columns represent: Sunday (index 0) to Saturday (index 6)
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# ============================ Start Session and Retrieve Cookies ============================
session = requests.Session()

# Access the main academic system page to obtain session cookies
url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": url_main
}
session.get(url_main, headers=headers)

# ============================ Define Academic Years and Semester ============================
academic_years = ["2022", "2023", "2024"]
semester_id = "2024-2025-2"

# API Endpoints for majors and classes
url_major = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
url_class = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

# ============================ Regular Expression for Classroom Extraction ============================
classroom_pattern = re.compile(r'(?:[ABCD]座\d{3}|外LanguageNetworkBuilding\d{3})(?!\d)')

# ============================ Function to Extract Classroom Names ============================
def extract_classrooms(course_text):
    """
    Extracts valid classroom names from course text.

    :param course_text: Raw text containing course details
    :return: List of extracted classroom names
    """
    classrooms = classroom_pattern.findall(course_text)  # Extract only valid classroom names
    return classrooms

# ============================ Fetch Data for Each Academic Year ============================
for year in academic_years:
    print(f"\nFetching majors for year {year}...")

    # Retrieve major list
    major_data = {"yxbh": "tc9qn3Xixg", "rxnf": year}
    response_major = session.post(url_major, data=major_data, headers=headers)

    if response_major.status_code != 200 or not response_major.text.strip():
        continue

    fixed_json_major = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_major.text)
    fixed_json_major = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_major)

    try:
        major_list = json.loads(fixed_json_major)
    except json.JSONDecodeError:
        continue

    for major in major_list:
        major_id = major["jx01id"]
        major_name = major["zymc"]

        class_data = {"yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id, "xnxq01id": semester_id}
        response_class = session.post(url_class, data=class_data, headers=headers)

        if response_class.status_code != 200 or not response_class.text.strip():
            continue

        fixed_json_class = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_class.text)
        fixed_json_class = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_class)

        try:
            class_list = json.loads(fixed_json_class)
        except json.JSONDecodeError:
            continue

        for class_info in class_list:
            class_id = class_info["xx04id"]
            class_name = class_info["bj"]

            schedule_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
            schedule_data = {
                "type": "xx04",
                "isview": "1",
                "xx04id": class_id,
                "yxbh": "tc9qn3Xixg",
                "rxnf": year,
                "zy": major_id,
                "bjbh": class_name,
                "zc": "1",
                "xnxq01id": semester_id,
                "xx04mc": "",
                "sfFD": "1"
            }

            response_schedule = session.post(schedule_url, data=schedule_data, headers=headers)

            if response_schedule.status_code != 200 or not response_schedule.text.strip():
                continue

            soup = BeautifulSoup(response_schedule.text, "html.parser")
            table = soup.find("table")

            if table:
                rows = table.find_all("tr")[1:]  # Skip header row
                for row_idx, row in enumerate(rows):
                    cols = row.find_all("td")

                    if len(cols) < 2:
                        continue

                    time_period = list(timetable.keys())[row_idx]

                    for col_idx in range(1, 8):  # Ensure processing for 7 days (Sunday-Saturday)
                        if col_idx >= len(cols):
                            continue

                        room_text = cols[col_idx].text.strip()
                        if not room_text:
                            continue

                        rooms = extract_classrooms(room_text)
                        if rooms:
                            # Append new classroom names instead of overwriting
                            if timetable[time_period][col_idx - 1]:
                                timetable[time_period][col_idx - 1] += ", " + ", ".join(rooms)
                            else:
                                timetable[time_period][col_idx - 1] = ", ".join(rooms)

# ============================ Print Final Classroom Schedule ============================
print("\nFinal Consolidated Classroom Usage:")
for time_slot, schedule in timetable.items():
    print([time_slot] + schedule)
