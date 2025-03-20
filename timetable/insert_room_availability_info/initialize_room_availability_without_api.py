import pymysql
from datetime import datetime, timedelta

# ============================ MySQL Connection Configuration ============================
# Configure MySQL connection
host = 'localhost'  # Database host address
user = 'root'  # MySQL username
password = '1234'  # MySQL password
database = 'booking_system_db'  # Target database name, ensure the database exists

# Create database connection
def get_db_connection():
    return pymysql.connect(host=host, user=user, password=password, database=database)

# Define room time slots (available time slots for each room)
availability_times = [
    ("08:00", "08:45"),
    ("08:55", "09:40"),
    ("10:00", "10:45"),
    ("10:55", "11:40"),
    ("14:00", "14:45"),
    ("14:55", "15:40"),
    ("16:00", "16:45"),
    ("16:55", "17:40"),
    ("19:00", "19:45"),
    ("19:55", "20:40")
]

# Function to insert room availability data
def insert_room_availability():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Get all room_ids
    cursor.execute("SELECT room_id FROM Rooms")
    rooms = cursor.fetchall()

    # Get today's date and calculate all dates for this week (from Monday to Sunday)
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday's date this week
    dates_this_week = [start_of_week + timedelta(days=i) for i in range(7)]  # All 7 days of the week

    # Insert room availability records for each room and time slot
    try:
        for room in rooms:
            room_id = room[0]

            # Insert records for each time slot and date for the current room
            for start_time, end_time in availability_times:
                for date in dates_this_week:
                    cursor.execute(""" 
                        INSERT INTO Room_availability (room_id, available_begin, available_end, available_date, availability) 
                        VALUES (%s, %s, %s, %s, 0)  -- Set availability to 0 (not available)
                    """, (room_id, start_time, end_time, date.strftime('%Y-%m-%d')))

        # Commit transaction
        connection.commit()
        print("Room availability records have been successfully inserted!")

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        connection.rollback()

    finally:
        # Close database connection
        cursor.close()
        connection.close()

# Run the insertion function directly
if __name__ == '__main__':
    insert_room_availability()
