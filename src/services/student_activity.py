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

def get_student_activities(student_id):
    """获取学生活动记录"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        activities = []

        try:
            # 获取学生提交记录
            cursor.execute("""
                SELECT
                    s.id,
                    s.problem_id,
                    s.submission_time,
                    s.submit_result,
                    p.title as problem_title
                FROM edu_coding_submissions s
                JOIN edu_problems p ON s.problem_id = p.id
                WHERE s.student_id = %s
                ORDER BY s.submission_time DESC
                LIMIT 10
            """, (student_id,))

            submission_results = cursor.fetchall()
            for submission in submission_results:
                result = '成功' if submission['submit_result'] == 'success' else '失败'
                activities.append({
                    'id': submission['id'],
                    'type': '提交代码',
                    'description': f"{submission['problem_title']} - {result}",
                    'time': submission['submission_time']
                })
        except Exception as inner_e:
            print(f"获取学生提交记录失败: {str(inner_e)}", file=sys.stderr)

        try:
            # 获取学生提问记录
            cursor.execute("""
                SELECT id, title, created_at
                FROM edu_questions
                WHERE student_email = (
                    SELECT email FROM edu_profiles_student WHERE student_id = %s
                )
                ORDER BY created_at DESC
                LIMIT 5
            """, (student_id,))

            question_results = cursor.fetchall()
            for question in question_results:
                activities.append({
                    'id': question['id'],
                    'type': '提问',
                    'description': question['title'],
                    'time': question['created_at']
                })
        except Exception as inner_e:
            print(f"获取学生提问记录失败: {str(inner_e)}", file=sys.stderr)

        # 如果没有获取到任何活动记录，返回空数组
        if not activities:
            print(f"警告: 未找到学生 {student_id} 的任何活动记录", file=sys.stderr)
            # 返回空数组，不使用假数据
            activities = []

        # 按时间排序
        activities.sort(key=lambda x: x['time'], reverse=True)

        # 只保留最近的10条记录
        activities = activities[:10]

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'activities': activities
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取学生活动记录失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def get_student_progress(student_id):
    """获取学生学习进度"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        try:
            # 获取所有章节
            cursor.execute("""
                SELECT
                    chapter_id,
                    chapter_title,
                    id as chapter_db_id
                FROM edu_teaching_contents
                ORDER BY id
            """)

            results = cursor.fetchall()

            if not results:
                # 如果没有获取到章节数据，返回空数组
                chapters = []
                print(f"警告: 未找到任何章节数据", file=sys.stderr)
            else:
                # 处理章节数据
                chapters = []

                for row in results:
                    chapter_id = row['chapter_id']

                    # 为每个章节创建6个默认小节
                    sections = []
                    for i in range(1, 7):
                        section_id = f"{chapter_id}-s{i}"
                        sections.append({
                            'id': section_id,
                            'title': f"小节 {i}",
                            'type': 'video'
                        })

                    # 创建章节对象
                    chapter = {
                        'chapter_id': chapter_id,
                        'chapter_title': row['chapter_title'],
                        'sections': sections,
                        'total_sections': 6,  # 每个章节默认6个小节
                        'completed_sections': 0
                    }

                    chapters.append(chapter)

                print(f"处理了 {len(chapters)} 个章节，每个章节默认6个小节", file=sys.stderr)

                # 获取已完成的小节
                try:
                    # 查询学生的已完成小节记录
                    print(f"正在查询学生ID为 {student_id} 的已完成小节记录...", file=sys.stderr)
                    cursor.execute("""
                        SELECT section_id
                        FROM edu_section_progress
                        WHERE student_id = %s
                    """, (student_id,))

                    completed_sections_results = cursor.fetchall()
                    completed_sections = [row['section_id'] for row in completed_sections_results]
                    print(f"学生ID为 {student_id} 的已完成小节数量: {len(completed_sections)}", file=sys.stderr)
                    print(f"已完成小节ID列表: {completed_sections}", file=sys.stderr)

                    # 计算每个章节的完成率
                    for chapter in chapters:
                        chapter_completed_sections = 0

                        for section in chapter['sections']:
                            if section['id'] in completed_sections:
                                chapter_completed_sections += 1

                        chapter['completed_sections'] = chapter_completed_sections

                        # 计算完成率
                        if chapter['total_sections'] > 0:
                            chapter['completion_rate'] = round((chapter_completed_sections / chapter['total_sections']) * 100, 1)
                        else:
                            chapter['completion_rate'] = 0
                except Exception as inner_e:
                    print(f"获取已完成小节失败: {str(inner_e)}", file=sys.stderr)
                    # 如果获取失败，将所有章节的完成率设为0
                    for chapter in chapters:
                        chapter['completed_sections'] = 0
                        chapter['completion_rate'] = 0
        except Exception as e:
            print(f"获取章节数据失败: {str(e)}", file=sys.stderr)
            # 返回空数组，不使用假数据
            chapters = []

        # 关闭数据库连接
        cursor.close()
        conn.close()

        # 返回结果
        print(json.dumps({
            'success': True,
            'data': {
                'chapters': chapters
            }
        }, cls=CustomJSONEncoder))

    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取学生学习进度失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'message': '缺少操作参数或学生ID'
        }), file=sys.stderr)
        sys.exit(1)

    operation = sys.argv[1]
    student_id = sys.argv[2]

    if operation == 'get_activities':
        get_student_activities(student_id)
    elif operation == 'get_progress':
        get_student_progress(student_id)
    else:
        print(json.dumps({
            'success': False,
            'message': f'未知操作: {operation}'
        }), file=sys.stderr)
