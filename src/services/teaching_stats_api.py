#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from datetime import datetime, timedelta
import traceback
import random

# 自定义JSON编码器，处理日期和Decimal类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        try:
            import decimal
            if isinstance(obj, decimal.Decimal):
                return float(obj)
        except ImportError:
            pass
        return super(CustomJSONEncoder, self).default(obj)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mwYgR7#*X2',
    'database': 'education_platform'
}

def get_teaching_stats():
    """获取教学统计数据"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 获取学生总数
        cursor.execute("""
            SELECT COUNT(*) as total_students
            FROM edu_profiles_student
        """)
        total_students_result = cursor.fetchone()
        total_students = total_students_result['total_students'] if total_students_result else 0

        # 获取上个月学生总数，计算增长率
        last_month = datetime.now() - timedelta(days=30)
        student_growth = 0

        try:
            cursor.execute("""
                SELECT COUNT(*) as last_month_students
                FROM edu_profiles_student
                WHERE created_at < %s
            """, (last_month,))
            last_month_result = cursor.fetchone()
            last_month_students = last_month_result['last_month_students'] if last_month_result else 0

            if last_month_students > 0:
                student_growth = round(((total_students - last_month_students) / last_month_students) * 100, 1)
        except Exception as inner_e:
            print(f"获取上个月学生总数失败: {str(inner_e)}", file=sys.stderr)
            # 不使用随机数据，保持增长率为0

        # 获取活跃学生数（过去7天有提交记录的学生）
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) as active_students
            FROM edu_coding_submissions
            WHERE submission_time >= %s
        """, (datetime.now() - timedelta(days=7),))
        active_students_result = cursor.fetchone()
        active_students = active_students_result['active_students'] if active_students_result else 0

        # 获取上周活跃学生数，计算增长率
        active_growth = 0
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) as last_week_active
            FROM edu_coding_submissions
            WHERE submission_time >= %s AND submission_time < %s
        """, (datetime.now() - timedelta(days=14), datetime.now() - timedelta(days=7)))
        last_week_result = cursor.fetchone()
        last_week_active = last_week_result['last_week_active'] if last_week_result else 0

        if last_week_active > 0:
            active_growth = round(((active_students - last_week_active) / last_week_active) * 100, 1)

        # 获取题目总数
        cursor.execute("""
            SELECT COUNT(*) as total_problems
            FROM edu_problems
        """)
        total_problems_result = cursor.fetchone()
        total_problems = total_problems_result['total_problems'] if total_problems_result else 0

        # 获取上个月题目总数，计算增长率
        problem_growth = 0
        try:
            cursor.execute("""
                SELECT COUNT(*) as last_month_problems
                FROM edu_problems
                WHERE created_at < %s
            """, (last_month,))
            last_month_problems_result = cursor.fetchone()
            last_month_problems = last_month_problems_result['last_month_problems'] if last_month_problems_result else 0

            if last_month_problems > 0:
                problem_growth = round(((total_problems - last_month_problems) / last_month_problems) * 100, 1)
        except Exception as inner_e:
            print(f"获取上个月题目总数失败: {str(inner_e)}", file=sys.stderr)
            # 不使用随机数据，保持增长率为0

        # 获取提交总数
        cursor.execute("""
            SELECT COUNT(*) as total_submissions
            FROM edu_coding_submissions
        """)
        total_submissions_result = cursor.fetchone()
        total_submissions = total_submissions_result['total_submissions'] if total_submissions_result else 0

        # 获取上周提交总数，计算增长率
        submission_growth = 0
        cursor.execute("""
            SELECT COUNT(*) as last_week_submissions
            FROM edu_coding_submissions
            WHERE submission_time < %s
        """, (datetime.now() - timedelta(days=7),))
        last_week_submissions_result = cursor.fetchone()
        last_week_submissions = last_week_submissions_result['last_week_submissions'] if last_week_submissions_result else 0

        if last_week_submissions > 0:
            submission_growth = round(((total_submissions - last_week_submissions) / last_week_submissions) * 100, 1)

        # 构建结果
        result = {
            'total_students': total_students,
            'student_growth': student_growth,
            'active_students': active_students,
            'active_growth': active_growth,
            'total_problems': total_problems,
            'problem_growth': problem_growth,
            'total_submissions': total_submissions,
            'submission_growth': submission_growth
        }

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取教学统计数据失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def get_activity_trend(time_range='week'):
    """获取活动趋势数据"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 确定日期范围
        if time_range == 'month':
            days = 30
            date_format = '%Y-%m-%d'
        else:  # 默认为周
            days = 7
            date_format = '%Y-%m-%d'

        # 生成日期列表
        dates = []
        date_values = []
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i-1)
            dates.append(date.strftime(date_format))
            date_values.append(date)

        # 获取每日提交次数
        submissions = [0] * days
        cursor.execute("""
            SELECT DATE(submission_time) as submission_date, COUNT(*) as submission_count
            FROM edu_coding_submissions
            WHERE submission_time >= %s
            GROUP BY submission_date
            ORDER BY submission_date
        """, (datetime.now() - timedelta(days=days),))

        submission_results = cursor.fetchall()
        for result in submission_results:
            submission_date = result['submission_date'].strftime(date_format)
            if submission_date in dates:
                index = dates.index(submission_date)
                submissions[index] = result['submission_count']

        # 获取每日提问次数
        questions = [0] * days
        cursor.execute("""
            SELECT DATE(created_at) as question_date, COUNT(*) as question_count
            FROM edu_questions
            WHERE created_at >= %s
            GROUP BY question_date
            ORDER BY question_date
        """, (datetime.now() - timedelta(days=days),))

        question_results = cursor.fetchall()
        for result in question_results:
            question_date = result['question_date'].strftime(date_format)
            if question_date in dates:
                index = dates.index(question_date)
                questions[index] = result['question_count']

        # 构建结果 - 不包含登录数据，因为没有真实数据
        result = {
            'dates': dates,
            'submissions': submissions,
            'questions': questions
        }

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取活动趋势数据失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def get_problem_completion():
    """获取题目完成情况数据 - 更科学的统计方法"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 获取题目难度分类
        cursor.execute("""
            SELECT DISTINCT difficulty
            FROM edu_problems
            ORDER BY
                CASE
                    WHEN difficulty = 'easy' THEN 1
                    WHEN difficulty = 'medium' THEN 2
                    WHEN difficulty = 'hard' THEN 3
                    WHEN difficulty = '1' THEN 1
                    WHEN difficulty = '2' THEN 2
                    WHEN difficulty = '3' THEN 3
                    ELSE 4
                END
        """)

        difficulty_results = cursor.fetchall()

        if not difficulty_results:
            # 如果没有获取到难度分类，返回错误
            cursor.close()
            conn.close()
            print(json.dumps({
                'success': False,
                'message': '没有找到题目难度分类数据'
            }), file=sys.stderr)
            return

        # 获取活跃学生总数（有提交记录的学生）
        cursor.execute("""
            SELECT COUNT(DISTINCT student_id) as active_students
            FROM edu_coding_submissions
        """)
        active_students_result = cursor.fetchone()
        active_students = active_students_result['active_students'] if active_students_result else 0

        if active_students == 0:
            # 如果没有活跃学生，返回错误
            cursor.close()
            conn.close()
            print(json.dumps({
                'success': False,
                'message': '没有找到活跃学生数据'
            }), file=sys.stderr)
            return

        # 准备结果数据结构
        difficulties = []
        difficulty_map = {}  # 用于映射难度名称

        # 统计指标
        student_completion_rates = []  # 学生平均完成率
        problem_attempt_rates = []     # 题目尝试率
        success_rates = []             # 提交成功率
        avg_attempts_per_problem = []  # 每题平均尝试次数

        for i, difficulty in enumerate(difficulty_results):
            diff = difficulty['difficulty']

            # 转换难度显示
            difficulty_name = diff
            if diff == 'easy' or diff == '1':
                difficulty_name = '简单'
            elif diff == 'medium' or diff == '2':
                difficulty_name = '中等'
            elif diff == 'hard' or diff == '3':
                difficulty_name = '困难'

            difficulties.append(difficulty_name)
            difficulty_map[diff] = difficulty_name

            # 获取该难度的题目总数
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM edu_problems
                WHERE difficulty = %s
            """, (diff,))

            total_result = cursor.fetchone()
            total_problems = total_result['total'] if total_result else 0

            if total_problems == 0:
                # 如果该难度没有题目，添加0值
                student_completion_rates.append(0)
                problem_attempt_rates.append(0)
                success_rates.append(0)
                avg_attempts_per_problem.append(0)
                continue

            # 1. 学生平均完成率 - 每个学生平均完成了该难度多少比例的题目
            cursor.execute("""
                SELECT
                    student_id,
                    COUNT(DISTINCT CASE WHEN submit_result = 'success' THEN problem_id END) as solved_problems
                FROM
                    edu_coding_submissions s
                JOIN
                    edu_problems p ON s.problem_id = p.id
                WHERE
                    p.difficulty = %s
                GROUP BY
                    student_id
            """, (diff,))

            student_results = cursor.fetchall()
            if not student_results:
                student_completion_rates.append(0)
            else:
                total_completion_rate = 0
                for student in student_results:
                    student_completion = (student['solved_problems'] / total_problems) * 100
                    total_completion_rate += student_completion

                avg_completion_rate = round(total_completion_rate / len(student_results), 1)
                student_completion_rates.append(avg_completion_rate)

            # 2. 题目尝试率 - 该难度有多少比例的题目至少被一名学生尝试
            cursor.execute("""
                SELECT COUNT(DISTINCT p.id) as attempted_problems
                FROM edu_problems p
                JOIN edu_coding_submissions s ON p.id = s.problem_id
                WHERE p.difficulty = %s
            """, (diff,))

            attempted_result = cursor.fetchone()
            attempted_problems = attempted_result['attempted_problems'] if attempted_result else 0
            attempt_rate = round((attempted_problems / total_problems) * 100, 1) if total_problems > 0 else 0
            problem_attempt_rates.append(attempt_rate)

            # 3. 提交成功率 - 该难度所有提交中成功的比例
            cursor.execute("""
                SELECT
                    COUNT(*) as total_submissions,
                    SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions
                FROM
                    edu_coding_submissions s
                JOIN
                    edu_problems p ON s.problem_id = p.id
                WHERE
                    p.difficulty = %s
            """, (diff,))

            submission_result = cursor.fetchone()
            if submission_result and submission_result['total_submissions'] > 0:
                success_rate = round((submission_result['successful_submissions'] / submission_result['total_submissions']) * 100, 1)
                success_rates.append(success_rate)
            else:
                success_rates.append(0)

            # 4. 每题平均尝试次数
            cursor.execute("""
                SELECT
                    p.id,
                    COUNT(*) as attempts
                FROM
                    edu_problems p
                JOIN
                    edu_coding_submissions s ON p.id = s.problem_id
                WHERE
                    p.difficulty = %s
                GROUP BY
                    p.id
            """, (diff,))

            problem_attempts = cursor.fetchall()
            if not problem_attempts:
                avg_attempts_per_problem.append(0)
            else:
                total_attempts = sum(p['attempts'] for p in problem_attempts)
                avg_attempts = round(total_attempts / len(problem_attempts), 1)
                avg_attempts_per_problem.append(avg_attempts)

        # 构建结果
        result = {
            'difficulties': difficulties,
            'student_completion_rates': student_completion_rates,  # 学生平均完成率
            'problem_attempt_rates': problem_attempt_rates,        # 题目尝试率
            'success_rates': success_rates,                        # 提交成功率
            'avg_attempts_per_problem': avg_attempts_per_problem,  # 每题平均尝试次数
            'active_students': active_students                     # 活跃学生总数
        }

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'data': result
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取题目完成情况数据失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def get_todos():
    """获取待处理事项"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        todos = []

        try:
            # 获取未回答的问题
            cursor.execute("""
                SELECT id, student_email, title, created_at
                FROM edu_questions
                WHERE answer IS NULL OR answer = ''
                ORDER BY created_at DESC
                LIMIT 5
            """)

            question_results = cursor.fetchall()
            for question in question_results:
                try:
                    # 获取学生姓名
                    cursor.execute("""
                        SELECT name
                        FROM edu_profiles_student
                        WHERE email = %s
                    """, (question['student_email'],))

                    student_result = cursor.fetchone()
                    student_name = student_result['name'] if student_result else question['student_email'].split('@')[0]

                    todos.append({
                        'id': question['id'],
                        'type': 'question',
                        'title': f'回答学生提问',
                        'description': f'{student_name}: {question["title"]}',
                        'time': question['created_at'],
                        'route': f'/teacher/answer?id={question["id"]}'
                    })
                except Exception as inner_e:
                    print(f"获取学生姓名失败: {str(inner_e)}", file=sys.stderr)
        except Exception as e:
            print(f"获取未回答问题失败: {str(e)}", file=sys.stderr)

        try:
            # 获取最近的提交记录
            cursor.execute("""
                SELECT s.id, s.student_id, s.problem_id, s.submission_time, p.title as problem_title
                FROM edu_coding_submissions s
                JOIN edu_problems p ON s.problem_id = p.id
                WHERE s.submit_result = 'success'
                ORDER BY s.submission_time DESC
                LIMIT 5
            """)

            submission_results = cursor.fetchall()
            for submission in submission_results:
                try:
                    # 获取学生姓名
                    cursor.execute("""
                        SELECT name
                        FROM edu_profiles_student
                        WHERE student_id = %s
                    """, (submission['student_id'],))

                    student_result = cursor.fetchone()
                    student_name = student_result['name'] if student_result else submission['student_id']

                    todos.append({
                        'id': submission['id'],
                        'type': 'submission',
                        'title': f'查看学生提交',
                        'description': f'{student_name} 完成了 {submission["problem_title"]}',
                        'time': submission['submission_time'],
                        'route': f'/teacher/data-analysis'
                    })
                except Exception as inner_e:
                    print(f"获取学生姓名失败: {str(inner_e)}", file=sys.stderr)
        except Exception as e:
            print(f"获取提交记录失败: {str(e)}", file=sys.stderr)

        # 按时间排序
        todos.sort(key=lambda x: x['time'], reverse=True)

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'todos': todos
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取待处理事项失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': '缺少操作参数'
        }), file=sys.stderr)
        sys.exit(1)

    operation = sys.argv[1]

    if operation == 'get_stats':
        get_teaching_stats()
    elif operation == 'get_activity_trend':
        time_range = sys.argv[2] if len(sys.argv) > 2 else 'week'
        get_activity_trend(time_range)
    elif operation == 'get_problem_completion':
        get_problem_completion()
    elif operation == 'get_todos':
        get_todos()
    else:
        print(json.dumps({
            'success': False,
            'message': f'未知操作: {operation}'
        }), file=sys.stderr)
