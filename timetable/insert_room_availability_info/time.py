from datetime import datetime
from datetime import datetime

# 获取当前日期
# current_date = datetime.today()
#
# # 获取当前年份
# current_year = current_date.year
#
# # 检查当前日期是否在9月1号之前
# if current_date.month < 9 or (current_date.month == 9 and current_date.day < 1):
#     # 当前日期在9月1号之前，academic_years不包括当前年
#     start_year = max(2022, current_year - 3)
#     academic_years = [str(year) for year in range(start_year, current_year)]
# else:
#     # 当前日期在9月1号之后，academic_years包括当前年
#     start_year = max(2022, current_year - 3)
#     academic_years = [str(year) for year in range(start_year, current_year + 1)]
#
# print(academic_years)
current_date = datetime.today().date()
print(current_date)
# 获取当前年份
current_year = current_date.today().year
print(current_year)
from datetime import datetime

# 获取当前日期
current_date = datetime.today()

# 获取当前年份
current_year = current_date.year

# 判断当前日期属于哪个学期
if (current_date.month >= 9 and current_date.month<=12):
    # 如果当前日期在9月1号到次年2月1号之间
    semester_id = f"{current_year}-{current_year + 1}-1"
elif (current_date.month == 1):
    semester_id = f"{current_year-1}-{current_year}-1"
elif (current_date.month >=2 and current_date.month<=8):
    # 如果当前日期在2月2号到8月31号之间
    semester_id = f"{current_year-1}-{current_year}-2"

print("当前学期的semester_id:", semester_id)

import csv
from datetime import datetime

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

# 读取 weeks.csv 文件
weeks = load_weeks('data/weeks.csv')

# 获取当前周次
current_week = get_current_week(weeks)
print(f"当前是第 {current_week} 周")

