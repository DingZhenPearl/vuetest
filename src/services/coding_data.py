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
    """获取学生编程统计数据 - 简化版，只返回题目ID和解决状态"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 只获取题目ID和是否已解决的状态
        cursor.execute("""
            SELECT
                problem_id,
                is_solved
            FROM edu_problem_solving_stats
            WHERE student_id = %s
        """, (student_id,))

        problem_details = cursor.fetchall()

        # 返回简化的数据
        result = {
            'student_id': student_id,
            'problem_details': problem_details
        }

        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))
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
        # 首先检查是否有该班级的数据
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM edu_coding_submissions
            WHERE student_class = %s
        """, (class_name,))

        count_result = cursor.fetchone()
        has_data = count_result and count_result['count'] > 0

        if not has_data:
            print(f"警告: 没有找到班级 '{class_name}' 的编程数据", file=sys.stderr)

            # 返回空数据结构
            result = {
                'class_name': class_name,
                'class_stats': {
                    'total_students': 0,
                    'total_problems': 0,
                    'total_submissions': 0,
                    'successful_submissions': 0,
                    'success_rate': 0
                },
                'problem_stats': [],
                'student_rankings': []
            }

            print(json.dumps({
                'success': True,
                'data': result,
                'message': f"没有找到班级 '{class_name}' 的编程数据"
            }, cls=CustomJSONEncoder))
            return

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

        class_stats = cursor.fetchone() or {
            'total_students': 0,
            'total_problems': 0,
            'total_submissions': 0,
            'successful_submissions': 0,
            'success_rate': 0
        }

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

        problem_stats = cursor.fetchall() or []

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

        student_rankings = cursor.fetchall() or []

        # 检查是否所有数据都为空
        all_empty = (
            class_stats['total_students'] == 0 and
            len(problem_stats) == 0 and
            len(student_rankings) == 0
        )

        if all_empty:
            print(f"警告: 所有查询都没有返回数据", file=sys.stderr)

        result = {
            'class_name': class_name,
            'class_stats': class_stats,
            'problem_stats': problem_stats,
            'student_rankings': student_rankings
        }

        print(json.dumps({
            'success': True,
            'data': result,
            'message': '获取编程数据成功' if not all_empty else '没有找到有效的编程数据'
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

def get_students_by_class(class_name):
    """从编程提交记录中获取班级所有学生"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 从编程提交记录中获取学生
        cursor.execute("""
            SELECT DISTINCT
                student_id,
                student_class as class_name
            FROM edu_coding_submissions
            WHERE student_class = %s
        """, (class_name,))

        students_from_submissions = cursor.fetchall()

        # 从解题统计中获取学生
        cursor.execute("""
            SELECT DISTINCT
                s.student_id,
                MAX(c.student_class) as class_name
            FROM edu_problem_solving_stats s
            JOIN edu_coding_submissions c ON s.student_id = c.student_id
            WHERE c.student_class = %s
            GROUP BY s.student_id
        """, (class_name,))

        students_from_stats = cursor.fetchall()

        # 合并两个来源的学生数据
        all_students = {}

        for student in students_from_submissions:
            all_students[student['student_id']] = {
                'student_id': student['student_id'],
                'class_name': student['class_name'],
                'name': student['student_id']  # 使用学号作为名称
            }

        for student in students_from_stats:
            if student['student_id'] not in all_students:
                all_students[student['student_id']] = {
                    'student_id': student['student_id'],
                    'class_name': student['class_name'],
                    'name': student['student_id']  # 使用学号作为名称
                }

        # 转换为列表
        students_list = list(all_students.values())

        print(json.dumps({
            'success': True,
            'students': students_list
        }, cls=CustomJSONEncoder))

    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取班级学生失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
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
    elif operation == "get_students_by_class" and len(sys.argv) > 2:
        get_students_by_class(sys.argv[2])
    elif operation == "create_tables":
        create_tables()
    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作或参数不足"
        }))