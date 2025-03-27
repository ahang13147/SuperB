import win32com.client
import psutil
import time
import os

def close_outlook():
    """关闭Outlook进程"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'OUTLOOK.EXE':
            print(f"正在关闭 Outlook (PID: {proc.info['pid']})...")
            proc.terminate()
            time.sleep(2)  # 等待2秒确保进程结束

def start_outlook():
    """重新启动Outlook应用"""
    print("重新启动 Outlook...")
    os.system('start outlook')  # 使用系统命令启动 Outlook
    time.sleep(10)  # 等待10秒，确保Outlook完全启动

def create_event(subject, start, end, busy, location='', reminder_minutes=15):
    """创建日历事件"""
    # 初始化Outlook
    outlook = win32com.client.Dispatch("Outlook.Application")
    appt = outlook.CreateItem(1)    # 1 = AppointmentItem

    appt.Start = start
    appt.Subject = subject
    appt.End = end
    appt.BusyStatus = busy
    appt.Location = location
    appt.MeetingStatus = 0  # 非会议事件

    # 设置提醒
    appt.ReminderSet = True
    appt.ReminderMinutesBeforeStart = reminder_minutes

    # 保存事件
    appt.Save()

    # 结束Outlook进程并重启
    close_outlook()
    start_outlook()

    # 重新打开Outlook并等待其加载
    time.sleep(5)  # 再次等待5秒钟，确保Outlook完全加载

    # 显示事件
    appt.Display()
    print(f"事件 '{subject}' 创建并显示完成!")

if __name__ == '__main__':
    # 示例调用
    create_event("Client Meeting", "2025-03-14 15:00", "2025-03-14 15:30", 0, "Teams", reminder_minutes=10)
