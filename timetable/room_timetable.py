import requests
from bs4 import BeautifulSoup
import json
import re
import time

"""
Description:
    This script retrieves the classroom schedule for all classes at Central South University's 
    Dundee International College (CSU). It extracts only the classroom names 
    and consolidates them into a structured timetable format.

Improvements:
    - Strict classroom name extraction: A座/B座/C座/D座+三位数 或 外语网络楼+三位数
    - Ensures timetable structure matches the expected format.
    - Appends multiple classrooms correctly instead of overwriting.
    - Enhances debugging for missing classrooms.

Author: Zibang Nie, Xin Yu, Siyan Guo
Version: 2025-03-04
"""

# ============================ 初始化课表结构 ============================
# 7 列分别表示：周日（索引 0）至周六（索引 6）
timetable = {
    "1-2": [""] * 7,
    "3-4": [""] * 7,
    "5-6": [""] * 7,
    "7-8": [""] * 7,
    "9-10": [""] * 7,
    "11-12": [""] * 7,
    "备注": [""] * 7
}

# ============================ 开启会话，获取 Cookie ============================
session = requests.Session()

# 访问教务系统的主页面以获取 session cookies
url_main = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&isview=1&xnxq01id=null"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": url_main
}
session.get(url_main, headers=headers)

# ============================ 定义学年和学期 ============================
academic_years = ["2022", "2023", "2024"]
xnxq01id = "2024-2025-2"

# 查询专业和班级的 API 地址
url_zy = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=queryzy"
url_bj = "http://csujwc.its.csu.edu.cn/KbctjcAction.do?method=querybj"

# ============================ 教室提取的正则匹配 ============================
classroom_pattern = re.compile(r'(?:[ABCD]座\d{3}|外语网络楼\d{3})(?!\d)')

# ============================ 提取教室信息的函数 ============================
def extract_classrooms(course_text):
    """
    从课程文本中提取教室信息，只保留严格符合格式的教室名。

    :param course_text: 课程信息文本
    :return: 提取出的教室列表
    """
    classrooms = classroom_pattern.findall(course_text)  # 只匹配严格格式
    return classrooms


# ============================ 遍历所有学年，获取课表数据 ============================
for year in academic_years:
    print(f"\nFetching majors for year {year}...")

    # 获取专业列表
    data_zy = {"yxbh": "tc9qn3Xixg", "rxnf": year}
    response_zy = session.post(url_zy, data=data_zy, headers=headers)

    if response_zy.status_code != 200 or not response_zy.text.strip():
        continue

    fixed_json_text = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_zy.text)
    fixed_json_text = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text)

    try:
        major_list = json.loads(fixed_json_text)
    except json.JSONDecodeError:
        continue

    for major in major_list:
        major_id = major["jx01id"]
        major_name = major["zymc"]

        data_bj = {"yxbh": "tc9qn3Xixg", "rxnf": year, "zy": major_id, "xnxq01id": xnxq01id}
        response_bj = session.post(url_bj, data=data_bj, headers=headers)

        if response_bj.status_code != 200 or not response_bj.text.strip():
            continue

        fixed_json_text_bj = re.sub(r"([{,])\s*([a-zA-Z0-9_]+)\s*:", r'\1"\2":', response_bj.text)
        fixed_json_text_bj = re.sub(r":\s*'([^']*)'", r':"\1"', fixed_json_text_bj)

        try:
            class_list = json.loads(fixed_json_text_bj)
        except json.JSONDecodeError:
            continue

        for class_info in class_list:
            class_id = class_info["xx04id"]
            class_name = class_info["bj"]

            post_url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
            form_data = {
                "type": "xx04",
                "isview": "1",
                "xx04id": class_id,
                "yxbh": "tc9qn3Xixg",
                "rxnf": year,
                "zy": major_id,
                "bjbh": class_name,
                "zc": "1",
                "xnxq01id": xnxq01id,
                "xx04mc": "",
                "sfFD": "1"
            }

            response_kb = session.post(post_url, data=form_data, headers=headers)

            if response_kb.status_code != 200 or not response_kb.text.strip():
                continue

            soup = BeautifulSoup(response_kb.text, "html.parser")
            table = soup.find("table")

            if table:
                rows = table.find_all("tr")[1:]  # 跳过表头
                for row_idx, row in enumerate(rows):
                    cols = row.find_all("td")

                    if len(cols) < 2:
                        continue

                    time_period = list(timetable.keys())[row_idx]

                    for col_idx in range(1, 8):  # 确保处理 7 天的数据
                        if col_idx >= len(cols):
                            continue

                        room_text = cols[col_idx].text.strip()
                        if not room_text:
                            continue

                        rooms = extract_classrooms(room_text)
                        if rooms:
                            # 追加而不是覆盖已有教室信息
                            if timetable[time_period][col_idx - 1]:
                                timetable[time_period][col_idx - 1] += ", " + ", ".join(rooms)
                            else:
                                timetable[time_period][col_idx - 1] = ", ".join(rooms)

# ============================ 输出最终课表 ============================
print("\nFinal Consolidated Classroom Usage:")
for time_slot, schedule in timetable.items():
    print([time_slot] + schedule)
