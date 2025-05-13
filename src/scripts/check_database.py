#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import json

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mwYgR7#*X2',
    'database': 'education_platform'
}

def check_teaching_contents():
    """检查教学内容表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询章节数据
        cursor.execute("SELECT * FROM edu_teaching_contents")
        chapters = cursor.fetchall()
        
        print(f"找到 {len(chapters)} 个章节:")
        for chapter in chapters:
            print(f"  章节ID: {chapter['chapter_id']}, 标题: {chapter['chapter_title']}")
        
        # 查询小节数据
        cursor.execute("SELECT * FROM edu_teaching_sections")
        sections = cursor.fetchall()
        
        print(f"\n找到 {len(sections)} 个小节:")
        for section in sections:
            print(f"  小节ID: {section['id']}, 章节ID: {section['chapter_id']}, 标题: {section['title']}")
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"检查教学内容表失败: {str(e)}")

def check_section_progress():
    """检查小节进度表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询小节进度数据
        cursor.execute("SELECT * FROM edu_section_progress")
        progress = cursor.fetchall()
        
        print(f"\n找到 {len(progress)} 条小节进度记录:")
        for p in progress:
            print(f"  学生ID: {p['student_id']}, 小节ID: {p['section_id']}, 完成时间: {p['completed_at']}")
        
        # 按学生ID分组统计
        cursor.execute("""
            SELECT student_id, COUNT(*) as count
            FROM edu_section_progress
            GROUP BY student_id
        """)
        stats = cursor.fetchall()
        
        print(f"\n学生小节完成统计:")
        for s in stats:
            print(f"  学生ID: {s['student_id']}, 已完成小节数: {s['count']}")
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"检查小节进度表失败: {str(e)}")

def check_student_profile():
    """检查学生个人信息表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 查询学生个人信息
        cursor.execute("SELECT * FROM edu_profiles_student")
        students = cursor.fetchall()
        
        print(f"\n找到 {len(students)} 个学生:")
        for student in students:
            print(f"  学生ID: {student['student_id']}, 姓名: {student.get('name', 'N/A')}")
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"检查学生个人信息表失败: {str(e)}")

if __name__ == '__main__':
    print("开始检查数据库...")
    check_teaching_contents()
    check_section_progress()
    check_student_profile()
    print("\n数据库检查完成。")
