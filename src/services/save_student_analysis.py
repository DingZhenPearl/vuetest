#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
保存学生AI分析结果
"""

import sys
import json
import mysql.connector
import traceback

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

def save_student_analysis(student_id, analysis_data):
    """保存学生AI分析结果"""
    print(f"开始保存学生AI分析结果，学生ID: {student_id}", file=sys.stderr)

    conn = None
    cursor = None

    try:
        # 解析分析数据
        try:
            if isinstance(analysis_data, str):
                analysis = json.loads(analysis_data)
            else:
                analysis = analysis_data
        except json.JSONDecodeError as e:
            print(f"解析分析数据失败: {str(e)}", file=sys.stderr)
            print(json.dumps({
                'success': False,
                'message': f"解析分析数据失败: {str(e)}"
            }))
            return

        # 检查必要字段
        required_fields = ['pattern', 'strengths', 'weaknesses', 'suggestions']
        for field in required_fields:
            if field not in analysis:
                print(f"分析数据缺少必要字段: {field}", file=sys.stderr)
                print(json.dumps({
                    'success': False,
                    'message': f"分析数据缺少必要字段: {field}"
                }))
                return

        conn = get_db_connection()
        if not conn:
            print(json.dumps({
                'success': False,
                'message': f"无法连接到数据库"
            }))
            return

        cursor = conn.cursor()

        # 插入分析结果
        cursor.execute("""
            INSERT INTO edu_student_ai_analysis
            (student_id, pattern, strengths, weaknesses, suggestions)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            student_id,
            analysis['pattern'],
            analysis['strengths'],
            analysis['weaknesses'],
            analysis['suggestions']
        ))

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "学生AI分析结果保存成功"
        }))
    except mysql.connector.Error as err:
        print(f"保存分析结果失败: {str(err)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"保存分析结果失败: {str(err)}"
        }))
    except Exception as e:
        print(f"保存分析结果时发生错误: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"保存分析结果时发生错误: {str(e)}"
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

    student_id = sys.argv[1]
    analysis_data = sys.argv[2]
    save_student_analysis(student_id, analysis_data)
