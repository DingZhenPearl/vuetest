#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from datetime import datetime

# 数据库连接配置
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

def create_tables():
    """创建必要的数据表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 学生编程数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_coding_submissions (
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
            CREATE TABLE IF NOT EXISTS edu_problem_solving_stats (
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
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "数据表创建成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"创建表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def submit_data(data_json_str):
    """处理提交的编程数据"""
    try:
        # 解析JSON数据
        data = json.loads(data_json_str)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 插入提交记录
        cursor.execute("""
            INSERT INTO edu_coding_submissions (
                student_class, student_id, problem_id, problem_title, 
                code_content, submit_result, execution_errors, 
                first_view_time, submission_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('student_class', ''),
            data['student_id'],
            data['problem_id'],
            data.get('problem_title', ''),
            data['code_content'],
            data['submit_result'],
            data.get('execution_errors'),
            data.get('first_view_time'),
            data.get('submission_time', datetime.now().isoformat())
        ))
        
        # 2. 更新解题统计
        # 查询是否已有此学生的此题统计
        cursor.execute("""
            SELECT * FROM edu_problem_solving_stats 
            WHERE student_id = %s AND problem_id = %s
        """, (data['student_id'], data['problem_id']))
        
        stats_record = cursor.fetchone()
        
        if not stats_record:
            # 创建新记录，确保first_view_time正确插入
            cursor.execute("""
                INSERT INTO edu_problem_solving_stats (
                    student_id, problem_id, total_attempts, 
                    is_solved, first_view_time
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                data['student_id'],
                data['problem_id'],
                1,  # 首次尝试
                data['submit_result'] == 'success',
                data.get('first_view_time')  # 确保此处使用提交的first_view_time
            ))
            
            # 如果一次就成功，记录解决时间
            if data['submit_result'] == 'success':
                cursor.execute("""
                    UPDATE edu_problem_solving_stats
                    SET solved_time = %s,
                        attempts_until_success = 1,
                        time_spent_seconds = TIMESTAMPDIFF(SECOND, first_view_time, %s)
                    WHERE student_id = %s AND problem_id = %s AND first_view_time IS NOT NULL
                """, (
                    data.get('submission_time'),
                    data.get('submission_time'),
                    data['student_id'],
                    data['problem_id']
                ))
        else:
            # 更新现有记录
            cursor.execute("""
                UPDATE edu_problem_solving_stats
                SET total_attempts = total_attempts + 1,
                    first_view_time = COALESCE(first_view_time, %s)
                WHERE student_id = %s AND problem_id = %s
            """, (data.get('first_view_time'), data['student_id'], data['problem_id']))
            
            # 如果之前未解决，但现在成功了
            if not stats_record[5] and data['submit_result'] == 'success':
                cursor.execute("""
                    UPDATE edu_problem_solving_stats
                    SET is_solved = TRUE,
                        solved_time = %s,
                        attempts_until_success = total_attempts,
                        time_spent_seconds = TIMESTAMPDIFF(SECOND, first_view_time, %s)
                    WHERE student_id = %s AND problem_id = %s AND first_view_time IS NOT NULL
                """, (
                    data.get('submission_time'),
                    data.get('submission_time'),
                    data['student_id'],
                    data['problem_id']
                ))
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "编程数据提交成功"
        }))
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f"处理数据失败: {str(e)}"
        }))

def get_student_stats(student_id):
    """获取学生编程统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取基本统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_problems_attempted,
                SUM(CASE WHEN is_solved = TRUE THEN 1 ELSE 0 END) as problems_solved,
                AVG(attempts_until_success) as avg_attempts_until_success,
                AVG(time_spent_seconds) as avg_solving_time_seconds
            FROM edu_problem_solving_stats
            WHERE student_id = %s
        """, (student_id,))
        
        basic_stats = cursor.fetchone()
        
        # 获取每道题的详细情况
        cursor.execute("""
            SELECT 
                problem_id,
                problem_title,
                is_solved,
                attempts_until_success,
                total_attempts,
                time_spent_seconds
            FROM edu_problem_solving_stats ps
            JOIN (
                SELECT DISTINCT problem_id, problem_title 
                FROM edu_coding_submissions
                WHERE student_id = %s
            ) as titles ON ps.problem_id = titles.problem_id
            WHERE student_id = %s
        """, (student_id, student_id))
        
        problem_details = cursor.fetchall()
        
        # 获取错误类型统计
        cursor.execute("""
            SELECT 
                execution_errors,
                COUNT(*) as error_count
            FROM edu_coding_submissions
            WHERE student_id = %s AND execution_errors IS NOT NULL
            GROUP BY execution_errors
            ORDER BY error_count DESC
        """, (student_id,))
        
        error_stats = cursor.fetchall()
        
        # 返回综合数据
        result = {
            'student_id': student_id,
            'basic_stats': basic_stats,
            'problem_details': problem_details,
            'error_stats': error_stats
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取学生统计失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_class_stats(class_name):
    """获取班级编程统计数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取班级内所有学生ID
        cursor.execute("""
            SELECT DISTINCT student_id
            FROM edu_coding_submissions
            WHERE student_class = %s
        """, (class_name,))
        
        students = cursor.fetchall()
        student_ids = [s['student_id'] for s in students]
        
        # 获取班级总体统计
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT student_id) as total_students,
                COUNT(DISTINCT problem_id) as total_problems,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as total_successful_submissions,
                COUNT(*) as total_submissions,
                (SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as success_rate
            FROM edu_coding_submissions
            WHERE student_class = %s
        """, (class_name,))
        
        class_stats = cursor.fetchone()
        
        # 获取班级内各题目完成情况
        cursor.execute("""
            SELECT 
                problem_id,
                MAX(problem_title) as problem_title,
                COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN student_id END) as students_solved,
                COUNT(DISTINCT student_id) as students_attempted,
                (COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN student_id END) / COUNT(DISTINCT student_id)) * 100 as completion_rate
            FROM edu_coding_submissions
            WHERE student_class = %s
            GROUP BY problem_id
        """, (class_name,))
        
        problem_stats = cursor.fetchall()
        
        # 获取学生排名情况
        student_rankings = []
        for student_id in student_ids:
            cursor.execute("""
                SELECT 
                    student_id,
                    COUNT(DISTINCT CASE WHEN is_solved = TRUE THEN problem_id END) as problems_solved,
                    AVG(attempts_until_success) as avg_attempts
                FROM edu_problem_solving_stats
                WHERE student_id = %s
            """, (student_id,))
            
            student_stat = cursor.fetchone()
            if student_stat:
                student_rankings.append(student_stat)
        
        # 按解决问题数量排序
        student_rankings.sort(key=lambda x: x['problems_solved'], reverse=True)
        
        result = {
            'class_name': class_name,
            'class_stats': class_stats,
            'problem_stats': problem_stats,
            'student_rankings': student_rankings
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取班级统计失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_problem_stats(problem_id):
    """获取特定题目的提交统计"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取题目基本信息
        cursor.execute("""
            SELECT 
                problem_id,
                MAX(problem_title) as problem_title,
                COUNT(DISTINCT student_id) as students_attempted,
                COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN student_id END) as students_solved,
                COUNT(*) as total_submissions,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions
            FROM edu_coding_submissions
            WHERE problem_id = %s
        """, (problem_id,))
        
        basic_info = cursor.fetchone()
        
        # 获取各班级的提交统计
        cursor.execute("""
            SELECT 
                student_class,
                COUNT(DISTINCT student_id) as students_attempted,
                COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN student_id END) as students_solved,
                (COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN student_id END) / COUNT(DISTINCT student_id)) * 100 as completion_rate
            FROM edu_coding_submissions
            WHERE problem_id = %s
            GROUP BY student_class
        """, (problem_id,))
        
        class_stats = cursor.fetchall()
        
        # 获取常见错误类型
        cursor.execute("""
            SELECT 
                execution_errors,
                COUNT(*) as count
            FROM edu_coding_submissions
            WHERE problem_id = %s AND execution_errors IS NOT NULL
            GROUP BY execution_errors
            ORDER BY count DESC
            LIMIT 10
        """, (problem_id,))
        
        common_errors = cursor.fetchall()
        
        # 获取解题时间分布
        cursor.execute("""
            SELECT 
                time_spent_seconds,
                COUNT(*) as count
            FROM edu_problem_solving_stats
            WHERE problem_id = %s AND is_solved = TRUE
            GROUP BY time_spent_seconds
            ORDER BY time_spent_seconds ASC
        """, (problem_id,))
        
        solving_time_distribution = cursor.fetchall()
        
        result = {
            'problem_info': basic_info,
            'class_stats': class_stats,
            'common_errors': common_errors,
            'solving_time_distribution': solving_time_distribution
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取题目统计失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 确保数据表创建
    create_tables()
    
    # 解析命令行参数
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': "缺少操作参数"
        }))
        sys.exit(1)
    
    operation = sys.argv[1]
    
    if operation == "submit_data" and len(sys.argv) > 2:
        submit_data(sys.argv[2])
    elif operation == "get_student_stats" and len(sys.argv) > 2:
        get_student_stats(sys.argv[2])
    elif operation == "get_class_stats" and len(sys.argv) > 2:
        get_class_stats(sys.argv[2])
    elif operation == "get_problem_stats" and len(sys.argv) > 2:
        get_problem_stats(sys.argv[2])
    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作或参数不足"
        }))