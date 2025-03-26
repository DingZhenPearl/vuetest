#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from datetime import datetime, date
from decimal import Decimal

# 添加自定义JSON编码器
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mwYgR7#*X2',
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
                time_spent_seconds INT DEFAULT 0,  # 修改字段名
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
        print(f"收到数据: {data_json_str}", file=sys.stderr)
        data = json.loads(data_json_str)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 插入提交记录到edu_coding_submissions
            submissions_sql = """
                INSERT INTO edu_coding_submissions (
                    student_class, student_id, problem_id, problem_title,
                    code_content, submit_result, execution_errors,
                    first_view_time, submission_time
                ) VALUES (
                    %(student_class)s, %(student_id)s, %(problem_id)s,
                    %(problem_title)s, %(code_content)s, %(submit_result)s,
                    %(execution_errors)s, STR_TO_DATE(%(first_view_time)s, '%Y-%m-%d %H:%i:%s'),
                    STR_TO_DATE(%(submission_time)s, '%Y-%m-%d %H:%i:%s')
                )
            """
            cursor.execute(submissions_sql, data)
            submission_id = cursor.lastrowid
            
            # 2. 更新或插入解题统计到edu_problem_solving_stats
            stats_sql = """
                INSERT INTO edu_problem_solving_stats (
                    student_id, problem_id, total_attempts, 
                    is_solved, first_view_time, time_spent_seconds
                ) VALUES (
                    %(student_id)s, %(problem_id)s, 1,
                    %(is_solved)s, STR_TO_DATE(%(first_view_time)s, '%Y-%m-%d %H:%i:%s'),
                    %(coding_time)s
                )
                ON DUPLICATE KEY UPDATE
                    total_attempts = total_attempts + 1,
                    is_solved = CASE
                        WHEN is_solved = FALSE AND %(is_solved)s = TRUE
                        THEN TRUE
                        ELSE is_solved
                    END,
                    attempts_until_success = CASE
                        WHEN is_solved = FALSE AND %(is_solved)s = TRUE
                        THEN total_attempts + 1
                        ELSE attempts_until_success
                    END,
                    solved_time = CASE
                        WHEN is_solved = FALSE AND %(is_solved)s = TRUE
                        THEN STR_TO_DATE(%(submission_time)s, '%Y-%m-%d %H:%i:%s')
                        ELSE solved_time
                    END,
                    time_spent_seconds = time_spent_seconds + %(coding_time)s
            """
            
            stats_data = {
                'student_id': data['student_id'],
                'problem_id': data['problem_id'],
                'is_solved': data['submit_result'] == 'success',
                'first_view_time': data['first_view_time'],
                'submission_time': data['submission_time'],
                'coding_time': int(data.get('coding_time', 0))
            }
            
            cursor.execute(stats_sql, stats_data)
            conn.commit()
            
            print(json.dumps({
                'success': True,
                'message': "编程数据提交成功",
                'submission_id': submission_id
            }))
            
        except mysql.connector.Error as e:
            conn.rollback()
            raise e
            
    except Exception as e:
        error_msg = f"处理数据失败: {str(e)}"
        print(f"错误: {error_msg}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': error_msg
        }))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

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
        # 获取班级总体统计
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT student_id) as total_students,
                COUNT(DISTINCT problem_id) as total_problems,
                COUNT(*) as total_submissions,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions,
                ROUND(AVG(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) * 100, 2) as success_rate
            FROM edu_coding_submissions
            WHERE student_class = %s
        """, (class_name,))
        
        class_stats = cursor.fetchone()
        
        # 获取班级内各题目完成情况
        cursor.execute("""
            SELECT 
                problem_id,
                MAX(problem_title) as problem_title,
                COUNT(*) as total_attempts,
                COUNT(DISTINCT student_id) as students_attempted,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_attempts,
                ROUND(AVG(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) * 100, 2) as success_rate
            FROM edu_coding_submissions
            WHERE student_class = %s
            GROUP BY problem_id
            ORDER BY problem_id
        """, (class_name,))
        
        problem_stats = cursor.fetchall()
        
        # 获取学生排名情况
        cursor.execute("""
            SELECT 
                student_id,
                COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN problem_id END) as solved_problems,
                COUNT(*) as total_submissions,
                ROUND(AVG(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) * 100, 2) as success_rate
            FROM edu_coding_submissions
            WHERE student_class = %s
            GROUP BY student_id
            ORDER BY solved_problems DESC, success_rate DESC
        """, (class_name,))
        
        student_rankings = cursor.fetchall()
        
        result = {
            'class_name': class_name,
            'class_stats': class_stats,
            'problem_stats': problem_stats,
            'student_rankings': student_rankings
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))
        
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
                COUNT(DISTINCT student_id) as total_students,
                COUNT(*) as total_submissions,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions,
                ROUND(AVG(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) * 100, 2) as success_rate
            FROM edu_coding_submissions
            WHERE problem_id = %s
        """, (problem_id,))
        
        problem_info = cursor.fetchone()
        
        # 获取各班级的完成情况
        cursor.execute("""
            SELECT 
                student_class,
                COUNT(DISTINCT student_id) as students_attempted,
                COUNT(*) as total_attempts,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_attempts,
                ROUND(AVG(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) * 100, 2) as success_rate
            FROM edu_coding_submissions
            WHERE problem_id = %s
            GROUP BY student_class
            ORDER BY success_rate DESC
        """, (problem_id,))
        
        class_stats = cursor.fetchall()
        
        # 获取错误统计
        cursor.execute("""
            SELECT 
                execution_errors,
                COUNT(*) as count
            FROM edu_coding_submissions
            WHERE problem_id = %s AND submit_result = 'failed' AND execution_errors IS NOT NULL
            GROUP BY execution_errors
            ORDER BY count DESC
            LIMIT 10
        """, (problem_id,))
        
        common_errors = cursor.fetchall()
        
        # 获取解题时间分布
        cursor.execute("""
            SELECT 
                TIMESTAMPDIFF(MINUTE, first_view_time, submission_time) as solving_time,
                COUNT(*) as count
            FROM edu_coding_submissions
            WHERE problem_id = %s AND submit_result = 'success'
            AND first_view_time IS NOT NULL
            GROUP BY solving_time
            ORDER BY solving_time
        """, (problem_id,))
        
        solving_time_distribution = cursor.fetchall()
        
        result = {
            'problem_info': problem_info,
            'class_stats': class_stats,
            'common_errors': common_errors,
            'solving_time_distribution': solving_time_distribution
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))
        
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