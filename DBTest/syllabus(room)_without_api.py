from datetime import datetime, timedelta
import pytz
import csv
import requests
from bs4 import BeautifulSoup
import mysql.connector
from datetime import datetime, timedelta



# Define the Course class to store course information
class Course:
    def __init__(self, weekday, timeslot, course_name, room, course_date):
        self.weekday = weekday  # Day of the week
        self.timeslot = timeslot  # Course period number
        self.course_name = course_name  # Name of the course
        self.room = room  # Room number
        self.course_date = course_date  # Date of the course
        self.start_period, self.end_period = self.set_period(timeslot)  # Set start and end times

    def set_period(self, timeslot):
        # Set the start and end times according to the class period
        schedule = {
            1: ("08:00:00", "08:45:00"),
            2: ("08:55:00", "09:40:00"),
            3: ("10:00:00", "10:45:00"),
            4: ("10:55:00", "11:40:00"),
            5: ("14:00:00", "14:45:00"),
            6: ("14:55:00", "15:40:00"),
            7: ("16:00:00", "16:45:00"),
            8: ("16:55:00", "17:40:00"),
            9: ("19:00:00", "19:45:00"),
            10: ("19:55:00", "20:40:00"),
            11: ("21:00:00", "21:45:00"),
            12: ("21:55:00", "22:40:00")
        }
        return schedule.get(timeslot, ("", ""))  # Return the corresponding period for the given timeslot

    def __str__(self):
        return f"课程名称: {self.course_name}, 课程日期: {self.course_date}, " \
               f"节次: {self.timeslot}, 起始时间: {self.start_period}, 结束时间: {self.end_period}"


# Set HTTP request headers
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "csujwc.its.csu.edu.cn",
    "Origin": "http://csujwc.its.csu.edu.cn",
    "Referer": "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_jx0601.jsp?xnxq01id=&init=1&isview=1",
    "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 CrKey/1.54.250320 Edg/134.0.0.0",
}

# Define days from Sunday to Saturday
days = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

all_course = []
all_course_two_week=[]


# Read CSV file and store week-to-date mapping
def load_weeks(file_path):
    tz = pytz.timezone('Asia/Shanghai')
    weeks = []
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            week = {
                "week_number": int(row['week_number']),
                # Convert start_date and end_date to timezone-aware datetime
                "start_date": tz.localize(datetime.strptime(row['start_date'], "%Y-%m-%d")),
                "end_date": tz.localize(datetime.strptime(row['end_date'], "%Y-%m-%d"))
            }
            weeks.append(week)
    return weeks


# Calculate which week the current date belongs to
def get_current_week(weeks):
    # Use Beijing timezone
    tz = pytz.timezone('Asia/Shanghai')
    current_date = datetime.now(tz)

    for week in weeks:
        if week["start_date"] <= current_date <= week["end_date"]:
            return week["week_number"]
    return None  # Return None if the current date doesn't fall within any defined week


# Get the current semester based on current date
def get_current_semester():
    # Use Beijing timezone
    tz = pytz.timezone('Asia/Shanghai')
    current_date = datetime.now(tz)

    if (current_date.month >= 9 and current_date.month <= 12):
        semester_id = f"{current_year}-{current_year + 1}-1"
    elif (current_date.month == 1):
        semester_id = f"{current_year - 1}-{current_year}-1"
    elif (current_date.month >= 2 and current_date.month <= 8):
        semester_id = f"{current_year - 1}-{current_year}-2"
    return semester_id


# Use Beijing timezone
tz = pytz.timezone('Asia/Shanghai')
current_date = datetime.now(tz).date()

# Get the current year
current_year = current_date.today().year
# Read the current week from the file
weeks = load_weeks('../weeks.csv')
current_week = get_current_week(weeks)
current_semester = get_current_semester()


# Function to calculate the date of the given weekday in the current week
def get_course_date(weekday):
    # Use Beijing timezone
    tz = pytz.timezone('Asia/Shanghai')
    today_weekday = (current_date.weekday() + 1) % 7  # Monday = 0, Sunday = 6
    target_weekday = days.index(weekday)  # 0 for Sunday, 1 for Monday, ..., 6 for Saturday

    # Calculate date difference to find the correct weekday date
    if target_weekday >= today_weekday:
        # If target weekday is today or after, directly calculate target date
        days_difference = target_weekday - today_weekday
    else:
        # If target weekday has passed, ensure the date is still within this week
        days_difference = target_weekday - today_weekday

    # Compute the target date
    target_date = current_date + timedelta(days=days_difference)
    return target_date.strftime("%Y-%m-%d")

def get_course_date_next_week(weekday):
    # Use Beijing timezone
    tz = pytz.timezone('Asia/Shanghai')
    today_weekday = (current_date.weekday() + 1) % 7  # Monday = 0, Sunday = 6
    target_weekday = days.index(weekday)  # 0 for Sunday, 1 for Monday, ..., 6 for Saturday

    # Calculate date difference to find the correct weekday date
    if target_weekday >= today_weekday:
        # If target weekday is today or after, directly calculate target date
        days_difference = target_weekday - today_weekday
    else:
        # If target weekday has passed, ensure the date is still within this week
        days_difference = target_weekday - today_weekday

    # Compute the target date
    target_date = current_date + timedelta(days=days_difference) + timedelta(days=7)
    return target_date.strftime("%Y-%m-%d")


# Payload data template for HTTP POST request
payload_template = {
    'type': 'jx0601',
    'isview': '1',
    # 'zc': '1',
    'zc': '',
    'xnxq01id': '',
    # 'xnxq01id': '2024-2025-2',
    'xqid': '9',
    'jzwid': '906',
    'jx0601id': '',
    'jx0601mc': '',
    'sfFD': '1'
}

for access_week in [current_week,current_week+1]:
    for room_num in list(range(101, 109)) + list(range(116, 120)) + [635]:  # Include room 635
        # Generate classroomID and jx0601id for the current room
        room_str = str(room_num)
        payload = payload_template.copy()
        payload['classroomID'] = f"外语网络楼{room_str}"  # Classroom ID

        # Use a specific jx0601id if it's room 635
        if room_num == 635:
            payload['jx0601id'] = "FD014E6967DD43C3AD07F6FA695327D1"  # Special jx0601id
        else:
            payload['jx0601id'] = f"9060{room_str}"  # For other rooms, generate jx0601id based on rules

        payload['zc'] = access_week
        payload['xnxq01id'] = current_semester

        # Send POST request
        url = 'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp'
        print(f"请求房间 {room_str} 的课程数据...")
        response = requests.post(url, headers=headers, data=payload)

        # Check response status
        if response.status_code == 200:
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get table data
            table = soup.find('table', {'id': 'kbtable'})
            rows = table.find_all('tr')

            # Extract course data
            print(f"房间 {room_str} 的课程表:")
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) > 1:
                    time_slot = cols[0].text.strip()  # Get time slot text, e.g., "1-2", "3-4"

                    # Only process valid time slots
                    if "－" in time_slot:  # Ensure time slot format is valid
                        try:
                            time_slot_number = int(time_slot.split('－')[0])  # Get the numeric part of the time slot
                        except ValueError:
                            continue  # Skip invalid time slot (e.g., "Note")

                        for i in range(1, len(cols)):
                            course_cell = cols[i].find('div', class_='kbcontent1')
                            if course_cell and access_week == current_week:
                                course_name = course_cell.text.strip()
                                course_date = get_course_date(days[i - 1])  # Get the course date
                                course_obj = Course(days[i - 1], time_slot_number, course_name, room_str, course_date)
                                print("hhh1", course_obj.start_period, "hhh2", course_obj.end_period)
                                all_course.append(course_obj)  # Directly append the Course instance to all_course
                                # Also add the even-numbered slot (same content as the odd-numbered one)
                                course_obj = Course(days[i - 1], time_slot_number + 1, course_name, room_str, course_date)
                                all_course.append(course_obj)  # Append even-numbered slot course
                            if not course_cell and access_week == current_week:
                                all_course.append(Course(days[i - 1], time_slot_number, "", room_str, "", "", ""))
                                all_course.append(Course(days[i - 1], time_slot_number + 1, "", room_str, "", "", ""))
                            if course_cell and access_week == current_week+1:
                                course_name = course_cell.text.strip()
                                course_date = get_course_date_next_week(days[i - 1])  # Get the course date
                                course_obj = Course(days[i - 1], time_slot_number, course_name, room_str, course_date)
                                print("hhh1", course_obj.start_period, "hhh2", course_obj.end_period)
                                all_course.append(course_obj)  # Directly append the Course instance to all_course
                                # Also add the even-numbered slot (same content as the odd-numbered one)
                                course_obj = Course(days[i - 1], time_slot_number + 1, course_name, room_str, course_date)
                                all_course.append(course_obj)  # Append even-numbered slot course
                            if not course_cell and access_week == current_week+1:
                                all_course.append(Course(days[i - 1], time_slot_number, "", room_str, "", "", ""))
                                all_course.append(Course(days[i - 1], time_slot_number + 1, "", room_str, "", "", ""))

            print("-" * 50)

        else:
            print(f"请求失败，状态码: {response.status_code} for room {room_num}")

    # Filter out courses with empty names
    all_course = [course for course in all_course if course.course_name != '']
    all_course_two_week.extend(all_course)
    # Print all course information
    for course in all_course:
        print(course)

for course in all_course_two_week:
    print(course)
#-----------------------------DATABASE PROCESS---------------------------------------#
import mysql.connector

# Connect to the database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Database host
        user="root",       # Database username
        password="8e397a5310016d27",   # Database password
        database="booking_system_db",  # Database name
        ssl_disabled=True
    )

# Get room_id based on room name
def get_room_id_by_room_name(room_name):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT room_id FROM Rooms WHERE room_name = %s", (room_name,))
        room_id = cursor.fetchone()
        return room_id[0] if room_id else None
    finally:
        connection.close()

# Update the availability field to 1 in the Room_availability table
def update_room_availability(course):
    room_id = get_room_id_by_room_name(course.room)

    if room_id:
        connection = get_db_connection()
        try:
            cursor = connection.cursor()

            # Get start_period, end_period, and course_date from the course object
            start_time = course.start_period
            end_time = course.end_period
            course_date = course.course_date

            # Update the Room_availability table
            cursor.execute("""
                UPDATE Room_availability
                SET availability = 1
                WHERE room_id = %s
                AND available_begin = %s
                AND available_end = %s
                AND available_date = %s
            """, (room_id, start_time, end_time, course_date))

            connection.commit()
        finally:
            connection.close()

# Process each course and update its corresponding Room_availability record
for course in all_course:
    update_room_availability(course)

print("课程的房间预定状态更新完毕。")

