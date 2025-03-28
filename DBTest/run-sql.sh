#!/bin/bash

# 数据库配置
DB_USER="root"
DB_PASSWORD="8e397a5310016d27"
DB_NAME="booking_system_db"  # 你可以根据需要修改数据库名称

# SQL 文件路径
CREATE_FILE="create.sql"
ADVANCE_FILE="advanced.sql"
INSERT_FILE="insert.sql"

# 检查 SQL 文件是否存在
if [[ ! -f "$CREATE_FILE" || ! -f "$ADVANCE_FILE" || ! -f "$INSERT_FILE" ]]; then
  echo "错误：SQL 文件缺失，请确保以下文件存在："
  echo "- $CREATE_FILE"
  echo "- $ADVANCE_FILE"
  echo "- $INSERT_FILE"
  exit 1
fi

# 执行 create.sql
echo "正在执行 $CREATE_FILE..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SOURCE $CREATE_FILE"
if [[ $? -ne 0 ]]; then
  echo "错误：执行 $CREATE_FILE 失败"
  exit 1
fi

# 执行 advance.sql
echo "正在执行 $ADVANCE_FILE..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SOURCE $ADVANCE_FILE"
if [[ $? -ne 0 ]]; then
  echo "错误：执行 $ADVANCE_FILE 失败"
  exit 1
fi

# 执行 insert.sql
echo "正在执行 $INSERT_FILE..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SOURCE $INSERT_FILE"
if [[ $? -ne 0 ]]; then
  echo "错误：执行 $INSERT_FILE 失败"
  exit 1
fi

echo "所有 SQL 文件已成功执行！"