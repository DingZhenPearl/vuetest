#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习行为分析脚本
用于分析学生学习行为并生成个性化学习建议
"""

import sys
import json
import io
import re
import mysql.connector
from datetime import datetime, timedelta, date
from decimal import Decimal
from openai import OpenAI

# 设置标准输出和标准错误的编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 自定义JSON编码器，处理Decimal、datetime和date类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
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
    print(f"开始分析学生学习行为，学生ID: {student_id}", file=sys.stderr)

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

        # 获取学生学习数据
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

        learning_stats = cursor.fetchone()

        if not learning_stats:
            print(f"未找到学生学习数据，尝试创建默认数据...", file=sys.stderr)
            # 如果没有找到学习数据，创建一个默认的空数据结构
            learning_stats = {
                'student_id': student_id,
                'total_problems': 0,
                'solved_problems': 0,
                'avg_attempts': 0,
                'avg_time_spent': 0,
                'max_time_spent': 0,
                'min_time_spent': 0
            }

        # 获取学生按难度分类的解题情况
        print(f"查询学生按难度分类的解题情况...", file=sys.stderr)
        try:
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
        except mysql.connector.Error as err:
            print(f"查询难度分类数据失败: {str(err)}", file=sys.stderr)
            difficulty_stats = []

        # 获取学生常见错误类型
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

        # 获取学生最近一周的活动
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

        # 构建学习数据
        print(f"构建学习数据...", file=sys.stderr)
        learning_data = {
            'learning_stats': learning_stats,
            'difficulty_stats': difficulty_stats,
            'error_patterns': error_patterns,
            'recent_activity': recent_activity
        }

        # 使用AI分析学习行为
        print(f"使用AI分析学习行为...", file=sys.stderr)
        behavior_analysis = analyze_with_ai(learning_data)

        print(f"分析完成，返回结果...", file=sys.stderr)
        print(json.dumps({
            'success': True,
            'data': {
                'learning_data': learning_data,
                'behavior_analysis': behavior_analysis
            }
        }, cls=CustomJSONEncoder))

    except mysql.connector.Error as err:
        print(f"数据库错误: {str(err)}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"分析学习行为失败: {str(err)}"
        }))
    except Exception as e:
        print(f"未预期的错误: {str(e)}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"分析学习行为失败: {str(e)}"
        }))
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        print(f"分析过程结束", file=sys.stderr)

def analyze_with_ai(learning_data):
    """使用AI分析学习行为"""
    try:
        # 检查学习数据是否有效
        if not learning_data or not learning_data.get('learning_stats'):
            print(f"学习数据不完整", file=sys.stderr)
            raise Exception("学习数据不完整，无法进行AI分析")

        # 创建OpenAI客户端
        print(f"创建AI客户端...", file=sys.stderr)
        try:
            client = OpenAI(
                api_key="ipzotlGevNqQsafvWSXi:cooExiNRkHtQtHkkIqNk",
                base_url="https://spark-api-open.xf-yun.com/v1"
            )
        except Exception as e:
            print(f"创建AI客户端失败: {str(e)}", file=sys.stderr)
            raise Exception(f"创建AI客户端失败: {str(e)}")

        # 构建提示词
        print(f"构建AI提示词...", file=sys.stderr)
        prompt = f"""
请分析以下学生的学习行为数据，并提供详细的学习模式分析、优势领域、待提升领域和学习建议。

学习数据:
{json.dumps(learning_data, indent=2, cls=CustomJSONEncoder)}

请特别注意：
1. 学习模式分析部分需要详细描述学生的学习行为特征、学习风格和解题模式，不要只返回"学习模式分析"这个标题。
2. 分析内容应基于提供的学习数据，包括学生的解题时间、尝试次数、成功率等指标。
3. 如果数据不足，请说明"根据现有数据，学生的学习模式显示..."，而不是只返回标题。

请以JSON格式返回分析结果，格式如下:
{{
  "pattern": "详细的学习模式分析内容，不要只写标题",
  "strengths": "优势领域分析",
  "weaknesses": "待提升领域分析",
  "suggestions": "学习建议"
}}
"""

        # 调用AI接口
        print(f"调用AI接口...", file=sys.stderr)
        try:
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
            print(f"收到AI响应，长度: {len(ai_response)}", file=sys.stderr)

            try:
                # 尝试从AI响应中提取JSON
                # 处理可能包含```json和```的情况
                json_match = ai_response.strip()
                if json_match.startswith('```json'):
                    json_match = json_match[7:]  # 移除开头的```json
                if json_match.endswith('```'):
                    json_match = json_match[:-3]  # 移除结尾的```

                # 清理并解析JSON
                json_match = json_match.strip()

                try:
                    # 尝试直接解析JSON
                    behavior_analysis = json.loads(json_match)
                    print(f"成功解析AI响应为JSON", file=sys.stderr)

                    # 验证必要字段是否存在，如果不存在则添加默认值
                    if not behavior_analysis.get('pattern'):
                        behavior_analysis['pattern'] = "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。"
                    if not behavior_analysis.get('strengths'):
                        behavior_analysis['strengths'] = "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。"
                    if not behavior_analysis.get('weaknesses'):
                        behavior_analysis['weaknesses'] = "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。"
                    if not behavior_analysis.get('suggestions'):
                        behavior_analysis['suggestions'] = "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"

                    return behavior_analysis
                except json.JSONDecodeError as je:
                    print(f"直接解析JSON失败，尝试提取文本内容: {str(je)}", file=sys.stderr)

                    # 如果JSON解析失败，尝试从文本中提取内容
                    pattern = ""
                    strengths = ""
                    weaknesses = ""
                    suggestions = ""

                    # 提取学习模式分析
                    pattern_match = re.search(r'学习模式分析[：:]\s*([\s\S]*?)(?=优势领域[：:]|strengths[：:]|$)', ai_response, re.IGNORECASE)
                    if pattern_match:
                        pattern = pattern_match.group(1).strip()

                    # 如果提取的内容为空或者就是"学习模式分析"，尝试其他方式提取
                    if not pattern or pattern == "学习模式分析":
                        # 尝试查找"学习模式"相关内容
                        pattern_alt_match = re.search(r'学习模式[：:]\s*([\s\S]*?)(?=优势|strengths|$)', ai_response, re.IGNORECASE)
                        if pattern_alt_match:
                            pattern = pattern_alt_match.group(1).strip()

                    # 如果还是没有找到，尝试提取包含"学习模式"、"学习行为"或"学习风格"的段落
                    if not pattern or pattern == "学习模式分析":
                        paragraphs = re.split(r'\n\s*\n', ai_response)
                        for para in paragraphs:
                            para = para.strip()
                            if "学习模式" in para or "学习行为" in para or "学习风格" in para:
                                # 排除只包含标题的段落
                                if len(para) > 10 and not para.startswith("学习模式分析"):
                                    pattern = para
                                    break

                    # 如果仍然没有找到，尝试提取第一段非标题内容
                    if not pattern or pattern == "学习模式分析":
                        paragraphs = re.split(r'\n\s*\n', ai_response)
                        for para in paragraphs:
                            para = para.strip()
                            # 排除只包含标题的段落
                            if len(para) > 20 and not re.match(r'^[^：:]{1,10}[：:]', para):
                                pattern = para
                                break

                    # 记录提取结果
                    print(f"提取的学习模式分析内容: {pattern}", file=sys.stderr)

                    # 提取优势领域
                    strengths_match = re.search(r'优势领域[：:]\s*([\s\S]*?)(?=待提升领域[：:]|weaknesses[：:]|$)', ai_response, re.IGNORECASE)
                    if strengths_match:
                        strengths = strengths_match.group(1).strip()

                    # 提取待提升领域
                    weaknesses_match = re.search(r'待提升领域[：:]\s*([\s\S]*?)(?=学习建议[：:]|suggestions[：:]|$)', ai_response, re.IGNORECASE)
                    if weaknesses_match:
                        weaknesses = weaknesses_match.group(1).strip()

                    # 提取学习建议
                    suggestions_match = re.search(r'学习建议[：:]\s*([\s\S]*?)(?=$)', ai_response, re.IGNORECASE)
                    if suggestions_match:
                        suggestions = suggestions_match.group(1).strip()

                    # 构建分析结果
                    behavior_analysis = {
                        'pattern': pattern or "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。",
                        'strengths': strengths or "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。",
                        'weaknesses': weaknesses or "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。",
                        'suggestions': suggestions or "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
                    }

                    print(f"从文本中提取的分析结果: {behavior_analysis}", file=sys.stderr)
                    return behavior_analysis
            except Exception as e:
                print(f"解析AI响应失败: {str(e)}", file=sys.stderr)
                print(f"AI响应内容: {ai_response}", file=sys.stderr)

                # 返回默认分析结果
                return {
                    'pattern': "您尚未完成足够的习题，无法生成详细的学习模式分析。建议先完成一些基础习题，以便系统能够分析您的学习行为。",
                    'strengths': "暂无足够数据分析您的优势领域。请完成更多习题以获取详细分析。",
                    'weaknesses': "暂无足够数据分析您的待提升领域。请完成更多习题以获取详细分析。",
                    'suggestions': "建议从基础习题开始，逐步提高难度。定期练习，保持学习的连续性。尝试不同类型的题目，拓展知识面。"
                }
        except Exception as api_err:
            print(f"调用AI接口失败: {str(api_err)}", file=sys.stderr)
            raise Exception(f"调用AI接口失败: {str(api_err)}")

    except Exception as e:
        print(f"AI分析过程中发生未预期错误: {str(e)}", file=sys.stderr)
        raise Exception(f"AI分析过程中发生错误: {str(e)}")



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
