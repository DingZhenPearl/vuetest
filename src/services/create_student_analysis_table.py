#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建学生AI分析结果表
"""

import sys
import json
import mysql.connector

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mwYgR7#*X2',
            database='education_platform'
        )
        return conn
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"数据库连接失败: {str(err)}"
        }))
        sys.exit(1)

def create_student_analysis_table():
    """创建学生AI分析结果表"""
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        if not conn:
            print(json.dumps({
                'success': False,
                'message': f"无法连接到数据库"
            }))
            return

        cursor = conn.cursor()

        # 创建学生AI分析结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_student_ai_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                pattern TEXT NOT NULL,
                strengths TEXT NOT NULL,
                weaknesses TEXT NOT NULL,
                suggestions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (student_id),
                INDEX (created_at)
            )
        """)

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "学生AI分析结果表创建成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"创建表失败: {str(err)}"
        }))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    create_student_analysis_table()
