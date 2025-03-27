import datetime
import uuid
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ============================
# 1. 生成 ICS 文件
# ============================
# 设定事件详情
summary = "Meeting with team"
description = "Let's discuss the project updates."
location = "Online Meeting"
# 设置开始与结束时间，格式为：YYYYMMDDTHHMMSSZ（UTC时间）
dtstart = "20250321T100000Z"
dtend = "20250322T110000Z"
dtstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
uid = str(uuid.uuid4())

ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Your Company//Your Product//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
END:VEVENT
END:VCALENDAR
"""

# 将 ICS 内容写入文件
ics_filename = "event.ics"
with open(ics_filename, "w", encoding="utf-8") as f:
    f.write(ics_content)

print("ICS file generated:", ics_filename)

# ============================
# 2. 生成预填链接
# ============================
# 生成 Google Calendar 链接
google_base_url = "https://calendar.google.com/calendar/r/eventedit?"
google_params = {
    "text": summary,
    "dates": f"{dtstart}/{dtend}",
    "details": description,
    "location": location
}
google_calendar_link = google_base_url + urllib.parse.urlencode(google_params)
print("Google Calendar link:", google_calendar_link)

# 生成 Outlook Web 链接
outlook_base_url = "https://outlook.office.com/calendar/0/deeplink/compose?"
# Outlook 链接中时间格式为 ISO 8601 格式（例如：2025-03-21T10:00:00Z）
outlook_params = {
    "subject": summary,
    "startdt": "2025-03-21T10:00:00Z",
    "enddt": "2025-03-22T11:00:00Z",
    "body": description,
    "location": location
}
outlook_calendar_link = outlook_base_url + urllib.parse.urlencode(outlook_params)
print("Outlook Calendar link:", outlook_calendar_link)

# ============================
# 3. 构造并发送邮件
# ============================
# 邮件基本信息（请根据实际情况修改）
sender_email = "2530681892@qq.com"
receiver_email = "2542881@dundee.ac.uk"
subject = "Add Calendar Event – Meeting with team"
body_text = f"""Hi,

Please use one of the following options to add the event to your calendar:

1. Click the link for Google Calendar:
{google_calendar_link}

2. Click the link for Outlook Web Calendar:
{outlook_calendar_link}

3. Alternatively, you can open the attached ICS file with your calendar application.

Best regards,
Your Team
"""

# 构造邮件消息
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# 添加文本部分
message.attach(MIMEText(body_text, "plain"))

# 添加 ICS 附件
with open(ics_filename, "rb") as f:
    ics_attachment = MIMEApplication(f.read(), _subtype="ics")
ics_attachment.add_header("Content-Disposition", "attachment", filename=ics_filename)
message.attach(ics_attachment)

# SMTP 服务器配置（请替换成你的 SMTP 服务器信息）
smtp_server = "smtp.qq.com"   # 例如 smtp.office365.com
smtp_port = 587                    # 常用端口 587 或 465（SSL）
smtp_username = "2530681892@qq.com"
smtp_password = "gnpunomuoqwhechd"

# 发送邮件
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # 开启 TLS 加密
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully.")
except Exception as e:
    print("Error sending email:", e)
