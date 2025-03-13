import win32com.client

outlook = win32com.client.Dispatch("Outlook.Application")


def create_event(subject, start, end, busy, location=''):
    """
    subject: 主题
    start: 开始时间, 格式 "2022-06-05 10:10"
    start: 结束时间, 格式 "2022-06-05 10:10"
    busy: 是否忙碌的状态, 可选内容: 2: busy, 0: available
    location: 事件地点
    """
    appt = outlook.CreateItem(1)  # 1 = AppointmentItem
    appt.Start = start
    appt.Subject = subject
    appt.End = end
    # appt.Duration = duration  # 也可以不用End, 换成指定持续时长, 单位: 分钟
    appt.BusyStatus = busy
    appt.Location = location
    appt.MeetingStatus = 0  # olNonMeeting, 非会议, 只是个人事件

    appt.Save()
    appt.Send()


if __name__ == '__main__':
    create_event("给客户回电话", "2025-3-14 11:00", "2025-3-14 11:30", 1, "Teams")
