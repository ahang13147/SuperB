import os
import time
from datetime import datetime, timedelta


def create_ics_file(subject, start, end, busy, location='', reminder_minutes=15):
    """
    生成一个 .ics 文件并保存到本地

    subject: 主题
    start: 开始时间, 格式 "2022-06-05 10:10"
    end: 结束时间, 格式 "2022-06-05 10:10"
    busy: 是否忙碌的状态, 可选内容: BUSY 或 FREE
    location: 事件地点
    reminder_minutes: 提前几分钟提醒
    """
    # 将字符串格式的时间转换为 datetime 对象
    start_time = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end_time = datetime.strptime(end, "%Y-%m-%d %H:%M")

    # 将日期和时间转换为 iCalendar 格式
    start_ics = start_time.strftime("%Y%m%dT%H%M%S")
    end_ics = end_time.strftime("%Y%m%dT%H%M%S")

    # 计算提醒时间并转换为 iCalendar 格式
    reminder_time = start_time - timedelta(minutes=reminder_minutes)
    reminder_ics = reminder_time.strftime("%Y%m%dT%H%M%S")

    # 创建 .ics 文件内容
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Microsoft Corporation//Outlook 12.0 MIMEDIR//EN
BEGIN:VEVENT
UID:{int(time.time())}@example.com
DTSTAMP:{start_ics}Z
DTSTART:{start_ics}Z
DTEND:{end_ics}Z
SUMMARY:{subject}
LOCATION:{location}
DESCRIPTION:{subject}
STATUS:{busy}
BEGIN:VALARM
TRIGGER:-PT{reminder_minutes}M
DESCRIPTION:{subject} Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR"""

    # 保存为 .ics 文件
    ics_filename = f"{subject.replace(' ', '_')}.ics"
    with open(ics_filename, "w") as ics_file:
        ics_file.write(ics_content)

    print(f".ics 文件已创建: {ics_filename}")

    # 自动打开 .ics 文件并导入到 Outlook
    open_ics_in_outlook(ics_filename)


def open_ics_in_outlook(ics_filename):
    """通过 Outlook 自动导入 .ics 文件"""
    try:
        # 获取 .ics 文件的绝对路径
        ics_file_path = os.path.abspath(ics_filename)

        # 使用系统命令打开 .ics 文件，Outlook 会自动导入
        os.system(f'start outlook.exe "{ics_file_path}"')

        print(f"已成功导入事件到 Outlook 日历: {ics_file_path}")
    except Exception as e:
        print(f"导入事件失败: {str(e)}")


if __name__ == '__main__':
    # 示例调用
    create_ics_file("Client Meeting", "2025-03-14 15:00", "2025-03-14 15:30", "BUSY", "Teams", reminder_minutes=10)
