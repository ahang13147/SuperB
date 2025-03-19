import csv

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import mysql.connector
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS

# 创建 Flask 应用并启用 CORS 支持
app = Flask(__name__)
CORS(app)  # 启用跨域资源共享 (CORS)，避免跨域问题

# ============================ 数据库连接配置 ============================
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",  # 替换为你的数据库密码
    "database": "booking_system_db",
    "ssl_disabled": True  # 禁用 SSL 连接
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


# ============================ 工具函数 ============================
def get_week_dates():
    """计算本周每一天的日期（周一到周日）"""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ============================ 全局变量 ============================
# 初始化时间表：7列代表星期日（索引0）到星期六（索引6）
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# 课时与时间映射（不做任何改动）
class_periods = {
    "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
    "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
    "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
    "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
    "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
    "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
}

# 正则表达式，用于提取教室名称（例如：外语网络楼635）
classroom_pattern = re.compile(r'外语网络楼(\d{3})')


def extract_classrooms(course_text):
    """从课程文本中提取教室名称"""
    return classroom_pattern.findall(course_text)

# 读取CSV文件并存储周次与日期的对应关系
def load_weeks(file_path):
    weeks = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            week = {
                "week_number": int(row['week_number']),
                "start_date": datetime.strptime(row['start_date'], "%Y-%m-%d"),
                "end_date": datetime.strptime(row['end_date'], "%Y-%m-%d")
            }
            weeks.append(week)
    return weeks

# 计算当前日期属于哪一周
def get_current_week(weeks):
    current_date = datetime.today()
    for week in weeks:
        if week["start_date"] <= current_date <= week["end_date"]:
            return week["week_number"]
    return None  # 如果日期不在任何一周内
# ============================ 爬取数据部分 (保持原样) ============================
def crawl_data():
    """爬取各学年的专业、班级和课程表数据"""
    global timetable  # 使用全局 timetable
    class_usage = {}
    session = requests.Session()
    url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url_main
    }
    session.get(url_main, headers=headers)
    current_date = datetime.today().date()
    # current_year = current_date.today().year
    # academic_years = ["2022", "2023", "2024"]
    current_date = datetime.today().date()
    # 获取当前年份
    current_year = current_date.today().year
    #通过文件读取当前周次
    weeks = load_weeks('weeks.csv')
    current_week = get_current_week(weeks)
    # 检查当前日期是否在9月1号之前
    if current_date.month < 9 or (current_date.month == 9 and current_date.day < 1):
        # 当前日期在9月1号之前，academic_years不包括当前年
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year)]
    else:
        # 当前日期在9月1号之后，academic_years包括当前年
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year + 1)]

    if (current_date.month >= 9 and current_date.month <= 12):
        # 如果当前日期在9月1号到次年2月1号之间
        semester_id = f"{current_year}-{current_year + 1}-1"
    elif (current_date.month == 1):
        semester_id = f"{current_year - 1}-{current_year}-1"
    elif (current_date.month >= 2 and current_date.month <= 8):
        # 如果当前日期在2月2号到8月31号之间
        semester_id = f"{current_year - 1}-{current_year}-2"
    url_major = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
    url_class = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

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
                    "zc": current_week,
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
                    rows = table.find_all("tr")[1:]
                    for row_idx, row in enumerate(rows):
                        cols = row.find_all("td")
                        if len(cols) < 2:
                            continue
                        time_period = list(timetable.keys())[row_idx]
                        for col_idx in range(1, 8):
                            if col_idx >= len(cols):
                                continue
                            room_text = cols[col_idx].text.strip()
                            if not room_text:
                                continue
                            rooms = extract_classrooms(room_text)
                            if rooms:
                                if timetable[time_period][col_idx - 1]:
                                    timetable[time_period][col_idx - 1] += ", " + ", ".join(rooms)
                                else:
                                    timetable[time_period][col_idx - 1] = ", ".join(rooms)
                                for room in rooms:
                                    if room not in class_usage:
                                        class_usage[room] = []
                                    class_usage[room].append(f"周{col_idx} {time_period}")
    return class_usage


# ============================ 整合数据 ============================
def integrate_schedule(class_usage):
    classroom_schedule = {}
    for room, times in class_usage.items():
        time_slots = sorted(set(times))
        days_schedule = {i: [] for i in range(7)}
        for time in time_slots:
            day, period = time.split(" ")
            day_number = int(day[1]) - 1
            time_ranges = class_periods.get(period, [("Unknown Time", "Unknown Time")])
            for time_range in time_ranges:
                start_time, end_time = time_range
                days_schedule[day_number].append(f"{start_time}{end_time}")
        formatted_schedule = {}
        for day_idx in range(7):
            if days_schedule[day_idx]:
                formatted_schedule[day_idx] = sorted(days_schedule[day_idx])
        classroom_schedule[int(room)] = formatted_schedule

    room_2d_array = {}
    for room, schedule in classroom_schedule.items():
        room_2d_array[room] = [[""] * len(class_periods) for _ in range(7)]
        for day_idx, times in schedule.items():
            for time_idx, time in enumerate(times):
                room_2d_array[room][day_idx][time_idx] = time
    return room_2d_array


def format_schedule_data(new_room_2d_array):
    week_dates = get_week_dates()
    formatted_schedule = []
    for room, schedule in new_room_2d_array.items():
        for day_idx, day in enumerate(schedule):
            for time_slot in day:
                if time_slot:
                    start_time, end_time = time_slot.split("-")
                    formatted_schedule.append([room, week_dates[day_idx], start_time, end_time])
    return formatted_schedule


# ============================ 更新数据库 ============================
def update_room_availability(formatted_schedule):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        for entry in formatted_schedule:
            room_name, available_date, available_begin, available_end = entry  # 解包数据
            cursor.execute("SELECT room_id FROM Rooms WHERE room_name = %s", (room_name,))
            room_result = cursor.fetchone()
            if not room_result:
                continue
            room_id = room_result["room_id"]
            cursor.execute("""
                SELECT availability_id FROM Room_availability
                WHERE room_id = %s AND available_date = %s 
                AND available_begin = %s AND available_end = %s
            """, (room_id, available_date, available_begin, available_end))
            existing_availability = cursor.fetchone()
            if existing_availability:
                cursor.execute("""
                    UPDATE Room_availability 
                    SET availability = 1
                    WHERE availability_id = %s
                """, (existing_availability["availability_id"],))
            else:
                cursor.execute("""
                    INSERT INTO Room_availability (room_id, available_date, available_begin, available_end, availability)
                    VALUES (%s, %s, %s, %s, 1)
                """, (room_id, available_date, available_begin, available_end))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# ============================ `split_time_slots` 函数 ============================
def split_time_slots(data):
    """将存储的字符串数据拆分为单个时间段（去除所有中括号）"""
    new_data = {}
    for room, schedule in data.items():
        new_schedule = []
        for day in schedule:
            new_day = []
            for item in day:
                if item:
                    time_slots = item.split('][')
                    if len(time_slots) > 1:
                        for slot in time_slots:
                            clean_slot = slot.replace("[", "").replace("]", "")
                            new_day.append(clean_slot)
                    else:
                        new_day.append(item)
                else:
                    new_day.append('')  # 处理空值的情况
            new_schedule.append(new_day)
        new_data[room] = new_schedule
    return new_data


# ============================ Flask API 端点 ============================
@app.route('/run_scheduler', methods=['GET'])
def run_scheduler():
    try:
        # 执行爬取并更新数据库
        result = main_scheduler()
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================ 主调度函数 ============================
def main_scheduler():
    # 1. 爬取数据
    class_usage = crawl_data()
    # 2. 整合数据到二维数组
    room_2d_array = integrate_schedule(class_usage)
    # 3. 拆分时间段，去除中括号
    new_room_2d_array = split_time_slots(room_2d_array)
    # 4. 格式化数据，生成标准格式列表
    formatted_schedule = format_schedule_data(new_room_2d_array)
    # 5. 更新数据库
    update_room_availability(formatted_schedule)
    return "Crawling and updating database successfully!"


# 直接运行 Flask 应用
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
