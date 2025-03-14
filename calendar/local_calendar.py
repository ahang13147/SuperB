import win32com.client
import time

# 初始化Outlook
outlook = win32com.client.Dispatch("Outlook.Application")

def create_event(subject, start, end, busy, location='', reminder_minutes=15):
    """
    subject: 主题
    start: 开始时间, 格式 "2022-06-05 10:10"
    end: 结束时间, 格式 "2022-06-05 10:10"
    busy: 是否忙碌的状态, 可选内容: 2: busy, 0: available
    location: 事件地点
    reminder_minutes: 提前几分钟提醒
    """
    # 记录开始时间
    start_time = time.time()
    print("开始创建事件...")

    appt = outlook.CreateItem(1)    # 1 = AppointmentItem
    print(f"创建Item时间：{time.time() - start_time:.2f}秒")

    appt.Start = start
    appt.Subject = subject
    appt.End = end
    appt.BusyStatus = busy
    appt.Location = location
    appt.MeetingStatus = 0  # olNonMeeting, 非会议, 只是个人事件

    # 设置提醒
    appt.ReminderSet = True
    appt.ReminderMinutesBeforeStart = reminder_minutes
    print(f"设置提醒时间：{time.time() - start_time:.2f}秒")

    # 保存事件
    appt.Save()
    print(f"保存事件时间：{time.time() - start_time:.2f}秒")

    # 展示事件：使用 Display() 打开事件详情
    appt.Display()
    print("事件创建并显示完成!")

if __name__ == '__main__':
    create_event("给客户回电话", "2025-03-15 23:00", "2025-03-15 23:30", 0, "Teams", reminder_minutes=10)
