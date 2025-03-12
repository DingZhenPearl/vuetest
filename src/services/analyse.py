# -*- coding: utf-8 -*-
import json
import sys
import io
import mysql.connector
import decimal
from openai import OpenAI

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("Python解释器路径:", sys.executable)
print("模块搜索路径:", sys.path)

def analyze_data(data):
    client = OpenAI(
        # 控制台获取key和secret拼接，假使控制台获取的APIPassword是123456
        api_key="ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk", 
        base_url = 'https://spark-api-open.xf-yun.com/v1'
    )
    completion = client.chat.completions.create(
        model='lite', # 指定请求的版本
        messages=[
            {
                "role": "user",
                "content": f"请分析以下学生的编程数据，并在最后给出总结: {data}"
            }
        ]
    )
    # 提取纯文本内容
    result_content = completion.choices[0].message.content
    print(result_content)  # 直接输出内容，而非整个对象

# 连接到MySQL服务器
conn = mysql.connector.connect(
    host='localhost',       
    user='root',            
    password='sushiding'    
)
cursor = conn.cursor()

# 创建数据库
cursor.execute('CREATE DATABASE IF NOT EXISTS my_database')
cursor.execute('USE my_database')

# 创建新表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_name VARCHAR(255) NOT NULL,
        coding_accuracy DECIMAL(5, 2) NOT NULL,
        coding_time INT NOT NULL
    )
''')

# 查询数据
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

# 打印原始数据（验证）
print("原始数据库数据:")
for student in users:
    print(student)

# 将数据转换为 JSON 格式（处理 Decimal 类型）
users_list = []
for row in users:
    users_list.append({
        "id": row[0],
        "student_name": row[1],
        "coding_accuracy": float(row[2]),  # 关键修复点：Decimal → float
        "coding_time": row[3]
    })
users_json = json.dumps(users_list)

# 调用分析函数
analyze_data(users_json)

# 关闭连接
cursor.close()
conn.close()