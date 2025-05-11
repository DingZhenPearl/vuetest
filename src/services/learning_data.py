#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习数据处理脚本
用于获取学生学习数据和生成学习分析
"""

import sys
import json
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal

# 自定义JSON编码器，处理Decimal和datetime类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super(CustomJSONEncoder, self).default(obj)

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

def get_student_data(student_id):
    """获取学生学习数据"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取学生基本信息
        cursor.execute("""
            SELECT 
                p.student_id,
                p.name,
                p.class_name,
                p.major
            FROM edu_profiles p
            WHERE p.student_id = %s
        """, (student_id,))
        
        student_info = cursor.fetchone()
        
        if not student_info:
            print(json.dumps({
                'success': False,
                'message': f"未找到学生信息: {student_id}"
            }))
            return
        
        # 获取学生编程提交统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_submissions,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions,
                COUNT(DISTINCT problem_id) as total_problems,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) / COUNT(*) * 100 as success_rate
            FROM edu_coding_submissions
            WHERE student_id = %s
        """, (student_id,))
        
        submission_stats = cursor.fetchone()
        
        # 获取学生解题统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total_problems,
                SUM(CASE WHEN is_solved = 1 THEN 1 ELSE 0 END) as solved_problems,
                AVG(attempts_until_success) as avg_attempts,
                AVG(time_spent_seconds) as avg_time_spent
            FROM edu_problem_solving_stats
            WHERE student_id = %s
        """, (student_id,))
        
        problem_stats = cursor.fetchone()
        
        # 获取学生最近一周的活动
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT 
                DATE(submission_time) as submission_date,
                COUNT(*) as submission_count,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_count
            FROM edu_coding_submissions
            WHERE student_id = %s AND submission_time >= %s
            GROUP BY DATE(submission_time)
            ORDER BY submission_date
        """, (student_id, one_week_ago))
        
        recent_activity = cursor.fetchall()
        
        # 获取学生按难度分类的解题情况
        cursor.execute("""
            SELECT 
                p.difficulty,
                COUNT(DISTINCT cs.problem_id) as attempted_problems,
                SUM(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) > 0 as solved_problems
            FROM edu_coding_submissions cs
            JOIN edu_problems p ON cs.problem_id = p.id
            WHERE cs.student_id = %s
            GROUP BY p.difficulty
        """, (student_id,))
        
        difficulty_stats = cursor.fetchall()
        
        # 获取学生常见错误类型
        cursor.execute("""
            SELECT 
                SUBSTRING_INDEX(execution_errors, '\n', 1) as error_type,
                COUNT(*) as occurrence_count
            FROM edu_coding_submissions
            WHERE student_id = %s AND submit_result = 'failed' AND execution_errors IS NOT NULL
            GROUP BY error_type
            ORDER BY occurrence_count DESC
            LIMIT 5
        """, (student_id,))
        
        error_patterns = cursor.fetchall()
        
        # 计算学生统计数据
        completed_problems = problem_stats['solved_problems'] if problem_stats['solved_problems'] else 0
        total_problems = problem_stats['total_problems'] if problem_stats['total_problems'] else 0
        completion_rate = (completed_problems / total_problems * 100) if total_problems > 0 else 0
        
        # 构建学生统计数据
        student_stats = {
            'completed_problems': int(completed_problems),
            'total_problems': int(total_problems),
            'completion_rate': round(completion_rate, 2),
            'avg_attempts': round(float(problem_stats['avg_attempts']) if problem_stats['avg_attempts'] else 0, 2),
            'avg_time_spent': round(float(problem_stats['avg_time_spent']) if problem_stats['avg_time_spent'] else 0, 2),
            'total_learning_time': round(float(problem_stats['avg_time_spent'] * completed_problems / 60) if problem_stats['avg_time_spent'] and completed_problems else 0, 2),
            'pending_problems': int(total_problems - completed_problems)
        }
        
        # 构建结果
        result = {
            'student_info': student_info,
            'submission_stats': submission_stats,
            'problem_stats': problem_stats,
            'recent_activity': recent_activity,
            'difficulty_stats': difficulty_stats,
            'error_patterns': error_patterns,
            'student_stats': student_stats
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))
        
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取学生数据失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'message': "参数不足"
        }))
        return
    
    command = sys.argv[1]
    
    if command == 'get_student_data':
        student_id = sys.argv[2]
        get_student_data(student_id)
    else:
        print(json.dumps({
            'success': False,
            'message': f"未知命令: {command}"
        }))

if __name__ == "__main__":
    main()
