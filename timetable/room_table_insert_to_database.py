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

# ============================ Class Schedule ================================
# We'll use a dictionary to store class usage information
class_usage = {}

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
classroom_pattern = re.compile(r'(外语网络楼\d{3})(?!\d)')


# ============================ Function to Extract Classroom Names ============================
def extract_classrooms(course_text):
    """
    Extracts valid classroom names from course text.

    :param course_text: Raw text containing course details
    :return: List of extracted classroom names
    """
    classrooms = classroom_pattern.findall(course_text)  # Extract only valid classroom names
    return classrooms


# ============================ Class Period to Time Mapping ============================
# Mapping for class periods to actual times (each class period has two time slots)
class_periods = {
    "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
    "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
    "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
    "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
    "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
    "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
}

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

                            # Store the room and time slot in class_usage
                            for room in rooms:
                                if room not in class_usage:
                                    class_usage[room] = []
                                class_usage[room].append(f"周{col_idx} {time_period}")

# ============================ Consolidate Classroom Usage ============================
classroom_schedule = {}

for room, times in class_usage.items():
    time_slots = sorted(set(times))  # Remove duplicates and sort the times
    formatted_times = []

    # Create a list of time slots for each day
    days_schedule = {i: [] for i in range(7)}  # Days 0-6, where 0=Monday, 6=Sunday

    for time in time_slots:
        day, period = time.split(" ")
        day_number = int(day[1]) - 1  # Adjust for 0-based index (e.g., "周1" -> 0, "周2" -> 1)

        time_ranges = class_periods.get(period, [("Unknown Time", "Unknown Time")])

        # Instead of grouping all time ranges into one, now we add them separately
        for time_range in time_ranges:
            # Add the time range to the appropriate day
            days_schedule[day_number].append(f"{time_range[0]}{time_range[1]}")

    # Format the final output for each classroom
    formatted_schedule = []
    for day_idx in range(7):
        if days_schedule[day_idx]:
            # Join individual time ranges in the correct format, making sure each is in a separate []
            formatted_schedule.append(f"周{day_idx + 1}" + "".join(days_schedule[day_idx]))

    classroom_schedule[room] = "(" + ",".join(formatted_schedule) + ")"

# ============================ Print Consolidated Classroom Schedule ============================
print("\nConsolidated Classroom Usage:")
for room, times in classroom_schedule.items():
    print(f"{room} {times}")

