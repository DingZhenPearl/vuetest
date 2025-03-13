#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import json
import hashlib
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sushiding',
    'database': 'education_platform'
}

def get_db_connection():
    """建立数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"数据库连接失败: {str(err)}"
        }))
        sys.exit(1)

def init_database():
    """初始化所有数据表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 用户认证表
        # 学生表
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 教师表
        cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 学生个人信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS student_profiles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                student_id VARCHAR(50),
                class_name VARCHAR(100),
                major VARCHAR(100),
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (email)
            )
        """)
        
        # 聊天历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                title VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                messages JSON NOT NULL,
                INDEX (user_email)
            )
        ''')
        
        # 问题表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                status ENUM('pending', 'answered') DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                answer TEXT,
                answered_at TIMESTAMP NULL,
                follow_ups JSON
            )
        """)
        
        # 学生编程数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coding_submissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_class VARCHAR(100) NOT NULL,
                student_id VARCHAR(50) NOT NULL,
                problem_id VARCHAR(50) NOT NULL,
                problem_title TEXT NOT NULL,
                code_content TEXT NOT NULL,
                submit_result ENUM('success', 'failed') NOT NULL,
                execution_errors TEXT,
                first_view_time TIMESTAMP,
                submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (student_id),
                INDEX (problem_id),
                INDEX (student_class)
            )
        """)
        
        # 学生解题统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problem_solving_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                problem_id VARCHAR(50) NOT NULL,
                attempts_until_success INT DEFAULT 0,
                total_attempts INT DEFAULT 0,
                is_solved BOOLEAN DEFAULT FALSE,
                first_view_time TIMESTAMP,
                solved_time TIMESTAMP,
                time_spent_seconds INT DEFAULT 0,
                UNIQUE KEY (student_id, problem_id)
            )
        """)
        
        # 用户分析数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_name VARCHAR(255) NOT NULL,
                coding_accuracy DECIMAL(5, 2) NOT NULL,
                coding_time INT NOT NULL
            )
        ''')
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': '所有数据表初始化成功'
        }))
        
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"初始化数据表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("开始初始化数据库...")
    init_database()