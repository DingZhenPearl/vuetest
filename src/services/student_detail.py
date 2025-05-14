#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学生详情数据服务
"""

import sys
import json
import mysql.connector
from datetime import datetime, timedelta, date
import traceback
from decimal import Decimal

# 自定义JSON编码器，处理datetime、date和Decimal等类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return float(obj)
        elif obj is None:
            return None
        try:
            # 尝试将其他类型转换为字符串
            return str(obj)
        except:
            # 如果无法转换，返回一个默认值
            return None

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

def get_student_detail(student_id):
    """获取学生详细信息"""
    print(f"开始获取学生详细信息，学生ID: {student_id}", file=sys.stderr)

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

        cursor = conn.cursor(dictionary=True)

        # 1. 获取学生基本信息
        print(f"查询学生基本信息...", file=sys.stderr)
        cursor.execute("""
            SELECT
                student_id,
                name,
                class_name,
                major,
                email
            FROM edu_profiles_student
            WHERE student_id = %s
        """, (student_id,))

        student = cursor.fetchone()
        if not student:
            # 尝试从其他表获取学生信息
            cursor.execute("""
                SELECT DISTINCT
                    student_id,
                    student_class as class_name
                FROM edu_coding_submissions
                WHERE student_id = %s
            """, (student_id,))
            student = cursor.fetchone()

        if not student:
            print(json.dumps({
                'success': False,
                'message': f"未找到学生信息，学生ID: {student_id}"
            }))
            return

        # 2. 获取学生学习统计数据
        print(f"查询学生学习统计数据...", file=sys.stderr)
        cursor.execute("""
            SELECT
                ps.student_id,
                COUNT(DISTINCT ps.problem_id) as total_problems,
                SUM(CASE WHEN ps.is_solved = 1 THEN 1 ELSE 0 END) as solved_problems,
                AVG(ps.attempts_until_success) as avg_attempts,
                AVG(ps.time_spent_seconds) as avg_time_spent,
                MAX(ps.time_spent_seconds) as max_time_spent,
                MIN(CASE WHEN ps.is_solved = 1 THEN ps.time_spent_seconds ELSE NULL END) as min_time_spent
            FROM edu_problem_solving_stats ps
            WHERE ps.student_id = %s
            GROUP BY ps.student_id
        """, (student_id,))

        learning_stats = cursor.fetchone() or {}

        # 3. 获取学生按难度分类的解题情况
        print(f"查询学生按难度分类的解题情况...", file=sys.stderr)
        try:
            cursor.execute("""
                SELECT
                    p.difficulty,
                    COUNT(DISTINCT cs.problem_id) as attempted_problems,
                    CASE WHEN SUM(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) > 0 THEN 1 ELSE 0 END as solved_problems,
                    AVG(ps.time_spent_seconds) as avg_time_spent
                FROM edu_coding_submissions cs
                JOIN edu_problems p ON cs.problem_id = p.id
                LEFT JOIN edu_problem_solving_stats ps ON cs.student_id = ps.student_id AND cs.problem_id = ps.problem_id
                WHERE cs.student_id = %s
                GROUP BY p.difficulty
            """, (student_id,))

            difficulty_stats = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"查询难度分类数据失败: {str(err)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            difficulty_stats = []
            # 不要让这个错误中断整个流程

        # 4. 获取学生常见错误类型
        print(f"查询学生常见错误类型...", file=sys.stderr)
        try:
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
        except mysql.connector.Error as err:
            print(f"查询错误类型数据失败: {str(err)}", file=sys.stderr)
            error_patterns = []

        # 5. 获取学生最近一周的活动
        print(f"查询学生最近一周的活动...", file=sys.stderr)
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        try:
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
        except mysql.connector.Error as err:
            print(f"查询最近活动数据失败: {str(err)}", file=sys.stderr)
            recent_activity = []

        # 6. 获取学生题目完成情况
        print(f"查询学生题目完成情况...", file=sys.stderr)
        try:
            cursor.execute("""
                SELECT
                    ps.problem_id,
                    MAX(p.title) as problem_title,
                    MAX(ps.is_solved) as is_solved,
                    MAX(ps.attempts_until_success) as attempts,
                    MAX(ps.time_spent_seconds) as time_spent_seconds,
                    MAX(ps.solved_time) as submission_time
                FROM edu_problem_solving_stats ps
                LEFT JOIN edu_problems p ON ps.problem_id = p.id
                WHERE ps.student_id = %s
                GROUP BY ps.problem_id
                ORDER BY submission_time DESC
            """, (student_id,))

            problems = cursor.fetchall()

            # 如果没有从edu_problem_solving_stats获取到数据，尝试从edu_coding_submissions获取
            if not problems:
                print(f"从edu_problem_solving_stats未找到数据，尝试从edu_coding_submissions获取...", file=sys.stderr)
                cursor.execute("""
                    SELECT
                        cs.problem_id,
                        MAX(cs.problem_title) as problem_title,
                        MAX(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) as is_solved,
                        COUNT(*) as attempts,
                        NULL as time_spent_seconds,
                        MAX(cs.submission_time) as submission_time
                    FROM edu_coding_submissions cs
                    WHERE cs.student_id = %s
                    GROUP BY cs.problem_id
                    ORDER BY submission_time DESC
                """, (student_id,))

                problems = cursor.fetchall()

        except mysql.connector.Error as err:
            print(f"查询题目完成情况失败: {str(err)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            problems = []

        # 7. 获取学生已有的AI分析结果
        print(f"查询学生AI分析结果...", file=sys.stderr)
        try:
            cursor.execute("""
                SELECT
                    pattern,
                    strengths,
                    weaknesses,
                    suggestions,
                    created_at
                FROM edu_student_ai_analysis
                WHERE student_id = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (student_id,))

            ai_analysis = cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"查询AI分析结果失败: {str(err)}", file=sys.stderr)
            ai_analysis = None

        # 构建结果数据
        result = {
            'student': student,
            'learning_stats': learning_stats,
            'difficulty_stats': difficulty_stats,
            'error_patterns': error_patterns,
            'recent_activity': recent_activity,
            'problems': problems,
            'ai_analysis': ai_analysis
        }

        # 添加调试信息
        print(f"准备序列化结果数据...", file=sys.stderr)

        # 检查每个数据部分是否包含可能导致序列化问题的字段
        try:
            # 检查recent_activity中的日期字段
            for item in recent_activity:
                if 'submission_date' in item and isinstance(item['submission_date'], date):
                    print(f"发现date类型: {item['submission_date']}", file=sys.stderr)
                    # 将date转换为字符串
                    item['submission_date'] = item['submission_date'].strftime('%Y-%m-%d')

            # 检查problems中的日期字段
            for problem in problems:
                if 'submission_time' in problem and problem['submission_time'] is not None:
                    if isinstance(problem['submission_time'], date) or isinstance(problem['submission_time'], datetime):
                        print(f"发现日期类型: {problem['submission_time']}", file=sys.stderr)
                        # 将日期转换为字符串
                        if isinstance(problem['submission_time'], date):
                            problem['submission_time'] = problem['submission_time'].strftime('%Y-%m-%d')
                        else:
                            problem['submission_time'] = problem['submission_time'].strftime('%Y-%m-%d %H:%M:%S')

            # 尝试序列化结果
            print(json.dumps({
                'success': True,
                'data': result
            }, cls=CustomJSONEncoder))

        except Exception as e:
            print(f"序列化结果数据时发生错误: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

            # 返回简化的结果
            print(json.dumps({
                'success': True,
                'data': {
                    'student': student,
                    'message': '部分数据无法序列化，请联系管理员'
                }
            }, cls=CustomJSONEncoder))

    except Exception as e:
        print(f"获取学生详细信息时发生错误: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"获取学生详细信息失败: {str(e)}"
        }))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'message': "参数不足"
        }))
        sys.exit(1)

    action = sys.argv[1]

    if action == "get_student_detail":
        student_id = sys.argv[2]
        get_student_detail(student_id)
    else:
        print(json.dumps({
            'success': False,
            'message': f"未知操作: {action}"
        }))
        sys.exit(1)
