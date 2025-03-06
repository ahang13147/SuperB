import requests
from bs4 import BeautifulSoup
import json
import re
import time

"""
此脚本用于从中南大学的丹麦国际学院（Dundee International College）获取所有课程的教室时间表
该脚本只提取教室的名称，并将其整合到一个结构化的时间表格式中。

作者：Zibang Nie, Xin Yu, Siyan Guo
版本：2025-03-04
"""

# ============================ 初始化时间表 ============================
# 7列分别代表：星期日（索引0）到星期六（索引6）
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# ============================ 课程安排 ================================
# 使用字典来存储每个教室的使用信息
class_usage = {}

# ============================ 启动会话并获取Cookie ============================
session = requests.Session()

# 访问主页面以获取会话的cookie
url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": url_main
}
session.get(url_main, headers=headers)

# ============================ 定义学年和学期 ============================
academic_years = ["2022", "2023", "2024"]  # 定义要抓取的学年
semester_id = "2024-2025-2"  # 当前学期

# 获取专业和班级的API地址
url_major = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
url_class = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

# ============================ 正则表达式提取教室名称 ============================
# 匹配“外语网络楼”后跟着三位数字的教室名称
classroom_pattern = re.compile(r'外语网络楼(\d{3})')

# ============================ 提取教室名称的函数 ============================
def extract_classrooms(course_text):
    """
    从课程文本中提取有效的教室名称。

    :param course_text: 课程的原始文本
    :return: 提取到的教室名称列表
    """
    classrooms = classroom_pattern.findall(course_text)  # 使用正则提取教室名称
    return classrooms


# ============================ 课时与时间映射 ============================
# 将课时与实际时间（每个课时有两个时间段）进行映射
class_periods = {
    "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
    "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
    "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
    "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
    "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
    "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
}

# ============================ 获取每个学年的数据 ============================
for year in academic_years:
    print(f"\n正在获取 {year} 学年的专业数据...")

    # 获取专业列表
    major_data = {"yxbh": "tc9qn3Xixg", "rxnf": year}
    response_major = session.post(url_major, data=major_data, headers=headers)

    if response_major.status_code != 200 or not response_major.text.strip():
        continue

    fixed_json_major = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_major.text)
    fixed_json_major = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_major)

    try:
        major_list = json.loads(fixed_json_major)  # 将返回的专业数据转为JSON格式
    except json.JSONDecodeError:
        continue

    # 遍历每个专业
    for major in major_list:
        major_id = major["jx01id"]
        major_name = major["zymc"]

        # 获取班级数据
        class_data = {"yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id, "xnxq01id": semester_id}
        response_class = session.post(url_class, data=class_data, headers=headers)

        if response_class.status_code != 200 or not response_class.text.strip():
            continue

        fixed_json_class = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_class.text)
        fixed_json_class = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_class)

        try:
            class_list = json.loads(fixed_json_class)  # 将返回的班级数据转为JSON格式
        except json.JSONDecodeError:
            continue

        # 遍历每个班级
        for class_info in class_list:
            class_id = class_info["xx04id"]
            class_name = class_info["bj"]

            # 获取该班级的时间表
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

            # 使用BeautifulSoup解析HTML内容
            soup = BeautifulSoup(response_schedule.text, "html.parser")
            table = soup.find("table")

            if table:
                rows = table.find_all("tr")[1:]  # 跳过表头
                # 遍历每一行课程安排
                for row_idx, row in enumerate(rows):
                    cols = row.find_all("td")

                    if len(cols) < 2:
                        continue

                    # 根据行索引获取对应的课时
                    time_period = list(timetable.keys())[row_idx]

                    # 遍历每一天（星期日到星期六）
                    for col_idx in range(1, 8):
                        if col_idx >= len(cols):
                            continue

                        room_text = cols[col_idx].text.strip()
                        if not room_text:
                            continue

                        # 提取教室信息
                        rooms = extract_classrooms(room_text)
                        if rooms:
                            # 如果该时间段已经有教室，附加新的教室名称
                            if timetable[time_period][col_idx - 1]:
                                timetable[time_period][col_idx - 1] += ", " + ", ".join(rooms)
                            else:
                                timetable[time_period][col_idx - 1] = ", ".join(rooms)

                            # 将教室和时间段存储到 class_usage 中
                            for room in rooms:
                                if room not in class_usage:
                                    class_usage[room] = []
                                class_usage[room].append(f"周{col_idx} {time_period}")

# ============================ 整合教室使用情况 ============================
classroom_schedule = {}
for room, times in class_usage.items():
    # 去重并排序时间段
    time_slots = sorted(set(times))
    days_schedule = {i: [] for i in range(7)}  # 0-6，代表7天（0=周一，6=周日）

    # 为每个教室和时间段添加对应的时间范围
    for time in time_slots:
        day, period = time.split(" ")
        day_number = int(day[1]) - 1  # 将“周1”转换为0，“周2”转换为1
        time_ranges = class_periods.get(period, [("Unknown Time", "Unknown Time")])

        # 添加每个时间段到对应的日程安排
        for time_range in time_ranges:
            start_time, end_time = time_range
            days_schedule[day_number].append(f"{start_time}{end_time}")

    # 格式化每个教室的时间表
    formatted_schedule = {}
    for day_idx in range(7):
        if days_schedule[day_idx]:
            formatted_schedule[day_idx] = sorted(days_schedule[day_idx])  # 对每一天的时间段进行排序

    classroom_schedule[int(room)] = formatted_schedule

# ============================ 存储数据到二维数组 ============================
room_2d_array = {}

# 将每个教室的时间表存储到二维数组
for room, schedule in classroom_schedule.items():
    room_2d_array[room] = [[""] * len(class_periods) for _ in range(7)]  # 7天，每天对应多个时间段

    # 将每个时间段的安排存储到对应的时间表中
    for day_idx, times in schedule.items():
        for time_idx, time in enumerate(times):
            room_2d_array[room][day_idx][time_idx] = time

# 处理函数
def split_time_slots(data):
    new_data = {}

    for room, schedule in data.items():
        new_schedule = []

        for day in schedule:
            new_day = []
            for item in day:
                if item:
                    # 如果有多个时间段（用中括号分隔），拆开并添加到新列表
                    time_slots = item.split('][')
                    if len(time_slots) > 1:
                        for slot in time_slots:
                            # 修正时间段格式
                            if not slot.startswith('['):
                                slot = '[' + slot
                            if not slot.endswith(']'):
                                slot = slot + ']'
                            new_day.append(slot)
                    else:
                        new_day.append(item)
                else:
                    new_day.append('')
            new_schedule.append(new_day)

        new_data[room] = new_schedule

    return new_data


# 使用该函数处理原始数据
new_room_2d_array = split_time_slots(room_2d_array)
print(new_room_2d_array)
# 打印结果查看并显示房间号、星期几及具体时间段
days_of_week = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

for room, schedule in new_room_2d_array.items():
    print(f"\nRoom {room}:")
    for day_idx, day in enumerate(schedule):
        print(f"  {days_of_week[day_idx]}:")
        for time_idx, time in enumerate(day):
            if time:
                print(f"    时段 {time_idx + 1}: {time}")
            else:
                print(f"    时段 {time_idx + 1}: 空")


