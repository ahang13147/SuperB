from flask import Flask, request, render_template_string

app = Flask(__name__)

# 定义一个用于验证邮箱的正则表达式
import re


def validate_email(email):
    # 检查邮箱是否以 @dundee.ac.uk 结尾
    email_regex = r'^[a-zA-Z0-9._%+-]+@dundee\.ac\.uk$'
    return re.match(email_regex, email) is not None


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']

        if validate_email(email):
            return f"欢迎，{email}！你已成功登录。"
        else:
            return "错误：只能使用 @dundee.ac.uk 的邮箱登录！"

    return '''
        <form method="POST">
            邮箱地址：<input type="email" name="email" required>
            <input type="submit" value="登录">
        </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
