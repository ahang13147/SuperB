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

# ================================== Flask Application Setup ==================================
# Create a Flask application and enable CORS support
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS) to avoid cross-domain issues

# ============================ Database Connection Configuration ============================
# Database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",  # Replace with your database password
    "database": "booking_system_db",
    "ssl_disabled": True  # Disable SSL connection
}

def get_db_connection():
    return mysql.connector.connect(**db_config)


# ============================ Utility Functions ============================
def get_week_dates():
    """Calculate the dates for each day of the current week (from Monday to Sunday)"""
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    return [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]


# ============================ Global Variables ============================
# Initialize timetable: 7 columns represent Sunday (index 0) to Saturday (index 6)
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# Mapping of class periods to time ranges (do not modify)
class_periods = {
    "1-2": [("[08:00-08:45]", "[08:55-09:40]")],
    "3-4": [("[10:00-10:45]", "[10:55-11:40]")],
    "5-6": [("[14:00-14:45]", "[14:55-15:40]")],
    "7-8": [("[16:00-16:45]", "[16:55-17:40]")],
    "9-10": [("[19:00-19:45]", "[19:55-20:40]")],
    "11-12": [("[21:00-21:45]", "[21:55-22:40]")]
}

# Regular expression to extract classroom names (e.g., "Foreign Language Network Building 635")
classroom_pattern = re.compile(r'外语网络楼(\d{3})')


def extract_classrooms(course_text):
    """Extract classroom names from course text"""
    return classroom_pattern.findall(course_text)

# Read CSV file and store week-to-date mapping
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

# Calculate which week the current date belongs to
def get_current_week(weeks):
    current_date = datetime.today()
    for week in weeks:
        if week["start_date"] <= current_date <= week["end_date"]:
            return week["week_number"]
    return None  # If the date is not within any week

# ============================ Data Scraping Functionality (Keep unchanged) ============================
def crawl_data():
    """Scrape data for majors, classes, and schedules for each academic year"""
    global timetable  # Use global timetable
    class_usage = {}
    session = requests.Session()
    url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": url_main
    }
    session.get(url_main, headers=headers)
    current_date = datetime.today().date()
    # Get the current year
    current_year = current_date.today().year
    # Read the current week from the file
    weeks = load_weeks('timetable/insert_room_availability_info/data/weeks.csv')
    current_week = get_current_week(weeks)
    # Check if the current date is before September 1st
    if current_date.month < 9 or (current_date.month == 9 and current_date.day < 1):
        # If the date is before September 1st, academic_years do not include the current year
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year)]
    else:
        # If the date is after September 1st, academic_years include the current year
        start_year = max(2022, current_year - 3)
        academic_years = [str(year) for year in range(start_year, current_year + 1)]

    if (current_date.month >= 9 and current_date.month <= 12):
        # If the current date is between September 1st and February 1st next year
        semester_id = f"{current_year}-{current_year + 1}-1"
    elif (current_date.month == 1):
        semester_id = f"{current_year - 1}-{current_year}-1"
    elif (current_date.month >= 2 and current_date.month <= 8):
        # If the current date is between February 2nd and August 31st
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


# ============================ Data Integration ============================
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


# ============================ Update Database ============================
def update_room_availability(formatted_schedule):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)
    try:
        for entry in formatted_schedule:
            room_name, available_date, available_begin, available_end = entry  # Unpack data
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


# ============================ Split Time Slots ============================
def split_time_slots(data):
    """Split stored string data into individual time slots (remove all brackets)"""
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
                    new_day.append('')  # Handle empty values
            new_schedule.append(new_day)
        new_data[room] = new_schedule
    return new_data


# ============================ Flask API Endpoint ============================
@app.route('/run_scheduler', methods=['GET'])
def run_scheduler():
    try:
        # Run the scraping and database update process
        result = main_scheduler()
        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================ Main Scheduler Function ============================
def main_scheduler():
    # 1. Scrape data
    class_usage = crawl_data()
    # 2. Integrate data into 2D array
    room_2d_array = integrate_schedule(class_usage)
    # 3. Split time slots and remove brackets
    new_room_2d_array = split_time_slots(room_2d_array)
    # 4. Format data and generate the standard format list
    formatted_schedule = format_schedule_data(new_room_2d_array)
    # 5. Update database
    update_room_availability(formatted_schedule)
    return "Crawling and updating database successfully!"


# Run Flask application directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
