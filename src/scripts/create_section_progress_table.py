#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import json
import traceback

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mwYgR7#*X2',
    'database': 'education_platform'
}

def create_section_progress_table():
    """创建学习小节进度表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建学习小节进度表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_section_progress (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                section_id VARCHAR(50) NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_progress (student_id, section_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # 提交事务
        conn.commit()
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        print(json.dumps({
            'success': True,
            'message': '学习小节进度表创建成功'
        }))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'创建学习小节进度表失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def import_from_localstorage():
    """从localStorage导入学习进度数据"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 获取所有学生
        cursor.execute("SELECT student_id FROM edu_profiles_student")
        students = cursor.fetchall()
        
        print(f"找到 {len(students)} 个学生")
        
        # 这里我们无法直接访问localStorage，需要通过前端导入
        # 这个函数只是一个示例，实际导入需要通过前端API
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        print(json.dumps({
            'success': True,
            'message': '此函数仅为示例，实际导入需要通过前端API'
        }))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'导入学习进度数据失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

if __name__ == '__main__':
    create_section_progress_table()
