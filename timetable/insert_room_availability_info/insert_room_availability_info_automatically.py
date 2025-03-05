import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# ============================ Initialize Timetable ============================
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

class_usage = {}


# ============================ Helper Functions ============================
def extract_classrooms(course_text):
    classroom_pattern = re.compile(r'外语网络楼(\d{3})')
    classrooms = classroom_pattern.findall(course_text)
    return classrooms


def process_schedule():
    session = requests.Session()
    url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": url_main}
    session.get(url_main, headers=headers)

    academic_years = ["2022", "2023", "2024"]
    semester_id = "2024-2025-2"

    # API Endpoints
    url_major = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
    url_class = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

    # Mapping for class periods to actual times
    class_periods = {
        "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
        "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
        "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
        "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
        "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
        "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
    }

    classroom_schedule = {}

    for year in academic_years:
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
                schedule_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
                schedule_data = {
                    "type": "xx04", "isview": "1", "xx04id": class_id,
                    "yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id,
                    "xnxq01id": semester_id
                }

                response_schedule = session.post(schedule_url, data=schedule_data, headers=headers)

                if response_schedule.status_code != 200 or not response_schedule.text.strip():
                    continue

                soup = BeautifulSoup(response_schedule.text, "html.parser")
                table = soup.find("table")

                if table:
                    rows = table.find_all("tr")[1:]
                    for row_idx, row in enumerate(rows):
                        cols = row.find_all("td")

                        if len(cols) < 2:
                            continue

                        time_period = list(timetable.keys())[row_idx]
                        for col_idx in range(1, 8):  # For Sunday to Saturday
                            if col_idx >= len(cols):
                                continue

                            room_text = cols[col_idx].text.strip()
                            if not room_text:
                                continue

                            rooms = extract_classrooms(room_text)
                            if rooms:
                                for room in rooms:
                                    if room not in classroom_schedule:
                                        classroom_schedule[room] = []
                                    time_slot = class_periods.get(time_period)
                                    classroom_schedule[room].append((f"周{col_idx}", time_slot[0][0]))

    return classroom_schedule


# 主函数：直接调用并输出调试数据
if __name__ == "__main__":
    classroom_schedule = process_schedule()

    # 打印调试数据
    print("\n调试输出：教室排课信息")
    for room, schedule in classroom_schedule.items():
        print(f"教室 {room}:")
        for day_schedule in schedule:
            print(f"  {day_schedule[0]}: {day_schedule[1]}")
