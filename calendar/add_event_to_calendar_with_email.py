import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================
# 生成 Outlook Web Calendar 预填链接
# ============================
summary = "Meeting with team"
description = "Let's discuss the project updates."
location = "Online Meeting"

# Outlook 链接中时间格式为 ISO 8601 格式（例如：2025-03-21T10:00:00Z）
outlook_base_url = "https://outlook.office.com/calendar/0/deeplink/compose?"
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
# 构造并发送邮件
# ============================
sender_email = "2530681892@qq.com"
receiver_email = "2542881@dundee.ac.uk"
subject = "Add Calendar Event – Meeting with team"
body_text = f"""Hi,

Please use the following link to add the event to your Outlook Web Calendar:
{outlook_calendar_link}

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

# SMTP 服务器配置（请替换为您实际使用的 SMTP 信息）
smtp_server = "smtp.qq.com"   # 例如：smtp.office365.com
smtp_port = 587               # 常用端口 587 或 465（SSL）
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
