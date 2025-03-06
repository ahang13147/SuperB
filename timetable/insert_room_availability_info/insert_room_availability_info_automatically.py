import requests
from bs4 import BeautifulSoup
import json
import re
import time
import mysql.connector

# Initialize timetable
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "Notes": [""] * 7
}

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="booking_system_db"
)
cursor = db.cursor()


# Function to extract room numbers from the output (e.g., 外语网络楼635)
def extract_room_number(room_name):
    match = re.search(r'外语网络楼(\d+)', room_name)
    if match:
        return int(match.group(1))  # Return the numeric part as an integer
    return None


# Sample data: Classroom schedule
classroom_schedule = {
    "外语网络楼635": "周2[10:00-10:45][10:55-11:40],周3[14:00-14:45][14:55-15:40][16:00-16:45][16:55-17:40],周4[10:00-10:45][10:55-11:40][19:00-19:45][19:55-20:40]",

    # Add more rooms and their schedule as needed
}

# Loop through the room schedule and insert room availability
for room_name, schedule in classroom_schedule.items():
    room_id = extract_room_number(room_name)  # Get room_id from room_name

    if room_id is None:
        continue  # Skip if room_id extraction failed

    # Split the schedule by days (e.g., "周2[10:00-10:45][10:55-11:40]" => ["10:00-10:45", "10:55-11:40"])
    days_schedule = schedule.split(',')

    for day_schedule in days_schedule:
        # Extract the day and time ranges
        day_match = re.match(r'周(\d)\[(.*?)\]', day_schedule)

        if day_match:
            day = int(day_match.group(1))  # Get the day of the week (1-7)
            time_ranges = day_match.group(2).split('][')  # Extract multiple time ranges

            for time_range in time_ranges:
                # Extract start time and end time
                start_time, end_time = time_range.split('-')

                # Insert room availability into the Room_availability table
                cursor.execute("""
                    INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, is_available)
                    VALUES (%s, %s, %s, %s, %s)
                """, (room_id, start_time, end_time, f"2025-03-06",
                      True))  # Set the date as required, here assumed as "2025-03-06"

    db.commit()  # Commit the transaction

# Close the database connection
cursor.close()
db.close()
