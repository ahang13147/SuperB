import datetime
import win32com.client
import threading
import pythoncom

from icalendar import Calendar, Event


# 创建ICS事件数据
def create_ics():
    # 创建一个空的日历对象
    cal = Calendar()

    # 创建一个新的事件
    event = Event()

    # 设置事件的基本属性
    event.add('summary', '会议')
    event.add('dtstart', datetime.datetime(2025, 3, 15, 14, 30))  # 开始时间
    event.add('dtend', datetime.datetime(2025, 3, 15, 16, 30))  # 结束时间

    # 将事件添加到日历中
    cal.add_component(event)

    # 返回生成的icalendar数据
    return cal.to_ical()


# 导入ICS数据到Outlook
def import_ics_to_outlook(ics_data):
    try:
        # 初始化COM
        pythoncom.CoInitialize()

        # 获取Outlook应用对象
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        # 通过Outlook的日历导入ICS数据
        calendar_folder = namespace.GetDefaultFolder(9)  # 9代表日历文件夹
        calendar_item = calendar_folder.Items.Add()

        # 设置日历项的属性
        calendar_item.Subject = "会议"
        calendar_item.Start = datetime.datetime(2025, 3, 15, 14, 30)
        calendar_item.End = datetime.datetime(2025, 3, 15, 16, 30)

        calendar_item.Save()  # 保存事件到日历
        print("成功将ICS事件导入Outlook日历！")
    except Exception as e:
        print(f"导入出错：{e}")
    finally:
        # 取消COM初始化
        pythoncom.CoUninitialize()


# 多线程操作
def thread_function():
    # 创建ICS事件数据
    ics_data = create_ics()

    # 将ICS数据导入到Outlook
    import_ics_to_outlook(ics_data)


# 创建并启动一个新的线程
def main():
    print("主线程开始执行...")
    thread = threading.Thread(target=thread_function)
    thread.start()  # 启动线程
    thread.join()  # 等待线程完成

    print("主线程完成!")


# 运行主程序
if __name__ == "__main__":
    main()
