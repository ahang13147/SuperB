import requests
from bs4 import BeautifulSoup

# 定义Course类，用于存储课程信息
class Course:
    def __init__(self, weekday, timeslot, course_name, room):
        self.weekday = weekday  # 星期几
        self.timeslot = timeslot  # 第几节课
        self.course_name = course_name  # 课程名称
        self.room = room  # 房间号

    def __str__(self):
        return f"{self.timeslot}: {self.course_name} ({self.room})"

# 定义Timetable类，用于存储和显示整个课程表
class Timetable:
    def __init__(self):
        # 存储课程表，字典的键是星期几，值是课程列表
        self.timetable = {day: [] for day in ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]}

    def add_course(self, weekday, timeslot, course_name, room):
        # 向课程表中添加课程
        self.timetable[weekday].append(Course(weekday, timeslot, course_name, room))

    def display(self):
        # 打印表头
        print(f"{'时间/星期':<15}", end="")
        for day in self.timetable:
            print(f"{day:<20}", end="")
        print()

        # 打印每个时间段的课程
        for timeslot in range(1, 13):  # 假设最多有12个时间段
            print(f"{timeslot}－{timeslot + 1:<10}", end="")
            for day in self.timetable:
                # 筛选出当前时间段对应的课程
                courses = [f"{course.course_name} ({course.room})" for course in self.timetable[day] if course.timeslot == timeslot]
                print(f"{', '.join(courses):<20}", end="")
            print()

    def display_all_courses(self):
        # 输出所有课程
        print("所有课程：")
        for day in self.timetable:
            for course in self.timetable[day]:
                print(f"{course.weekday} - 第{course.timeslot}节: {course.course_name} (房间: {course.room})")

# 设置请求头
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

# 设置负载数据
payload = {
    'type': 'jx0601',
    'isview': '1',
    'zc': '9',
    'xnxq01id': '2024-2025-2',
    'xqid': '9',
    'jzwid': '906',
    'classroomID': '外语网络楼102',  # 这里指定了教室编号
    'jx0601id': '9060102',
    'jx0601mc': '',
    'sfFD': '1'
}
all_course=[]
# 从负载数据中提取房间号（直接使用classroomID中的数字部分）
room_number = payload['classroomID'].split('楼')[-1]  # 提取'117'作为房间号

# 发送POST请求
url = 'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp'
response = requests.post(url, headers=headers, data=payload)

# 检查响应状态码
if response.status_code == 200:
    # 解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取表格数据
    table = soup.find('table', {'id': 'kbtable'})
    rows = table.find_all('tr')

    # 初始化一个课程表对象
    timetable = Timetable()

    # 获取星期日到星期六
    days = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

    # 提取课程内容
    for row in rows[1:]:
        cols = row.find_all('td')
        if len(cols) > 1:
            time_slot = cols[0].text.strip()  # 获取时间段，如 1-2，3-4 等

            # 只处理有效的时间段
            if "－" in time_slot:  # 确保时间段文本有效
                try:
                    time_slot_number = int(time_slot.split('－')[0])  # 获取时间段的数字部分
                except ValueError:
                    continue  # 跳过无效时间段（如“备注”）

                for i in range(1, len(cols)):
                    course_cell = cols[i].find('div', class_='kbcontent1')
                    if course_cell:
                        course_name = course_cell.text.strip()
                        timetable.add_course(days[i - 1], time_slot_number, course_name, room_number)  # 使用room_number
                        all_course.append((days[i - 1], time_slot_number, course_name, room_number))
                    else:
                        timetable.add_course(days[i - 1], time_slot_number, "", room_number)  # 没有课程时填空

    # 打印课程表
    timetable.display()

    # 输出所有课程
    timetable.display_all_courses()

else:
    print(f"请求失败，状态码: {response.status_code}")

for course in all_course:
    print(course)