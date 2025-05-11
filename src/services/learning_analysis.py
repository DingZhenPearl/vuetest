#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习行为分析脚本
用于分析学生学习行为并生成个性化学习建议
"""

import sys
import json
import mysql.connector
from datetime import datetime, timedelta
from decimal import Decimal
from openai import OpenAI

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

def analyze_behavior(student_id):
    """分析学生学习行为"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 获取学生学习数据
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
        
        learning_stats = cursor.fetchone()
        
        if not learning_stats:
            print(json.dumps({
                'success': False,
                'message': f"未找到学生学习数据: {student_id}"
            }))
            return
        
        # 获取学生按难度分类的解题情况
        cursor.execute("""
            SELECT 
                p.difficulty,
                COUNT(DISTINCT cs.problem_id) as attempted_problems,
                SUM(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) > 0 as solved_problems,
                AVG(ps.time_spent_seconds) as avg_time_spent
            FROM edu_coding_submissions cs
            JOIN edu_problems p ON cs.problem_id = p.id
            LEFT JOIN edu_problem_solving_stats ps ON cs.student_id = ps.student_id AND cs.problem_id = ps.problem_id
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
        
        # 构建学习数据
        learning_data = {
            'learning_stats': learning_stats,
            'difficulty_stats': difficulty_stats,
            'error_patterns': error_patterns,
            'recent_activity': recent_activity
        }
        
        # 使用AI分析学习行为
        behavior_analysis = analyze_with_ai(learning_data)
        
        print(json.dumps({
            'success': True,
            'data': {
                'learning_data': learning_data,
                'behavior_analysis': behavior_analysis
            }
        }, cls=CustomJSONEncoder))
        
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"分析学习行为失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def analyze_with_ai(learning_data):
    """使用AI分析学习行为"""
    try:
        # 创建OpenAI客户端
        client = OpenAI(
            api_key="ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk", 
            base_url="https://spark-api-open.xf-yun.com/v1"
        )
        
        # 构建提示词
        prompt = f"""
请分析以下学生的学习行为数据，并提供详细的学习模式分析、优势领域、待提升领域和学习建议。

学习数据:
{json.dumps(learning_data, indent=2, cls=CustomJSONEncoder)}

请以JSON格式返回分析结果，格式如下:
{{
  "pattern": "学习模式分析",
  "strengths": "优势领域",
  "weaknesses": "待提升领域",
  "suggestions": "学习建议"
}}
"""
        
        # 调用AI接口
        completion = client.chat.completions.create(
            model="lite",
            messages=[
                {"role": "system", "content": "你是一个专业的教育顾问和学习行为分析专家，擅长分析学生的学习行为和表现，并提供个性化的学习建议。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # 解析AI响应
        ai_response = completion.choices[0].message.content
        
        try:
            # 尝试从AI响应中提取JSON
            json_match = ai_response.strip()
            behavior_analysis = json.loads(json_match)
            return behavior_analysis
        except json.JSONDecodeError:
            # 如果解析失败，返回默认分析
            return get_default_analysis()
            
    except Exception as e:
        print(f"AI分析失败: {str(e)}", file=sys.stderr)
        return get_default_analysis()

def get_default_analysis():
    """获取默认分析（当AI分析失败时使用）"""
    return {
        "pattern": "您的学习模式显示出一定的规律性，但可能需要更加系统化的学习计划。",
        "strengths": "您在解决简单和中等难度的问题上表现较好，能够坚持完成任务。",
        "weaknesses": "在处理复杂问题时可能需要更多的时间和尝试，错误处理能力有待提高。",
        "suggestions": "建议制定更有规律的学习计划，每天固定时间学习。针对常见错误类型进行专项练习，提高解决复杂问题的能力。多参考优秀解答，学习不同的解题思路。"
    }

def main():
    """主函数"""
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'message': "参数不足"
        }))
        return
    
    command = sys.argv[1]
    
    if command == 'analyze_behavior':
        student_id = sys.argv[2]
        analyze_behavior(student_id)
    else:
        print(json.dumps({
            'success': False,
            'message': f"未知命令: {command}"
        }))

if __name__ == "__main__":
    main()
