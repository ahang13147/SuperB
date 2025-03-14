from flask import Flask, request, jsonify
from flask_cors import CORS
import win32com.client
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 启用跨域请求支持

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
    print("正在创建事件...")
    # 记录开始时间
    start_time = time.time()

    try:
        # 将 start 和 end 字符串转换为 datetime 对象
        start_datetime = datetime.strptime(start, '%Y-%m-%dT%H:%M')  # 格式化为 datetime 对象
        end_datetime = datetime.strptime(end, '%Y-%m-%dT%H:%M')

        appt = outlook.CreateItem(1)  # 1 = AppointmentItem
        print(f"创建AppointmentItem耗时：{time.time() - start_time:.2f}秒")

        appt.Start = start_datetime.strftime('%Y-%m-%d %H:%M')  # 将 datetime 转换回字符串以供 Outlook 使用
        appt.Subject = subject
        appt.End = end_datetime.strftime('%Y-%m-%d %H:%M')
        appt.BusyStatus = busy
        appt.Location = location
        appt.MeetingStatus = 0  # olNonMeeting, 非会议, 只是个人事件

        # 设置提醒
        appt.ReminderSet = True
        appt.ReminderMinutesBeforeStart = reminder_minutes
        print(f"设置提醒耗时：{time.time() - start_time:.2f}秒")

        # 保存事件
        appt.Save()
        print(f"保存事件耗时：{time.time() - start_time:.2f}秒")

        # 展示事件：使用 Display() 打开事件详情
        appt.Display()
        print("事件创建并显示完成！")

        return "事件创建成功！"
    except Exception as e:
        print(f"创建事件时发生错误: {str(e)}")
        return str(e)


@app.route('/create_event', methods=['POST'])
def create_event_api():
    print("收到请求，开始处理...")

    # 从请求中获取数据
    data = request.json
    print(f"请求数据: {data}")

    subject = data.get('subject')
    start = data.get('start')
    end = data.get('end')
    busy = data.get('busy')
    location = data.get('location', '')
    reminder_minutes = data.get('reminder_minutes', 15)

    # 调用创建事件的函数
    try:
        result = create_event(subject, start, end, busy, location, reminder_minutes)
        print(f"事件创建成功: {result}")
        return jsonify({"message": result}), 200
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
