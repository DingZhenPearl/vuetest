#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
学习推荐脚本
用于生成个性化学习推荐和管理推荐状态
"""

import sys
import json
import mysql.connector
from datetime import datetime
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

def create_tables():
    """创建必要的数据表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建学习推荐表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_learning_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                priority ENUM('high', 'medium', 'low') NOT NULL,
                resources JSON,
                actionable BOOLEAN DEFAULT FALSE,
                problem_id VARCHAR(50),
                chapter_id VARCHAR(50),
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                INDEX (student_id),
                INDEX (chapter_id)
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

def save_recommendations(student_id, recommendations):
    """保存学习推荐到数据库"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print(f"开始为学生 {student_id} 保存 {len(recommendations)} 条学习推荐...", file=sys.stderr)

        # 先删除该学生未读的旧推荐
        cursor.execute("""
            DELETE FROM edu_learning_recommendations
            WHERE student_id = %s AND is_read = FALSE
        """, (student_id,))
        print(f"已删除学生 {student_id} 的旧推荐", file=sys.stderr)

        # 插入新推荐
        chapter_count = 0
        problem_count = 0

        for rec in recommendations:
            # 检查是否包含章节ID
            has_chapter = 'chapterId' in rec and rec['chapterId']
            has_problem = 'problemId' in rec and rec['problemId']

            if has_chapter:
                chapter_count += 1
                print(f"发现章节推荐: {rec['title']} -> 章节ID: {rec['chapterId']}", file=sys.stderr)

            if has_problem:
                problem_count += 1
                print(f"发现题目推荐: {rec['title']} -> 题目ID: {rec['problemId']}", file=sys.stderr)

            cursor.execute("""
                INSERT INTO edu_learning_recommendations
                (student_id, title, description, priority, resources, actionable, problem_id, chapter_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                rec['title'],
                rec['description'],
                rec['priority'],
                json.dumps(rec.get('resources', [])),
                rec.get('actionable', False),
                rec.get('problemId'),
                rec.get('chapterId')
            ))

        conn.commit()
        print(f"推荐保存成功，包含 {chapter_count} 条章节推荐和 {problem_count} 条题目推荐", file=sys.stderr)
        print(json.dumps({
            'success': True,
            'message': "推荐保存成功"
        }))
    except mysql.connector.Error as err:
        print(f"保存推荐失败: {str(err)}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"保存推荐失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_recommendations(student_id):
    """获取学生的学习推荐"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        print(f"开始获取学生 {student_id} 的学习推荐...", file=sys.stderr)

        # 获取未读的推荐
        cursor.execute("""
            SELECT
                id,
                title,
                description,
                priority,
                resources,
                actionable,
                problem_id as problemId,
                chapter_id as chapterId,
                created_at
            FROM edu_learning_recommendations
            WHERE student_id = %s AND is_read = FALSE
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                created_at DESC
        """, (student_id,))

        recommendations = cursor.fetchall()
        print(f"查询到 {len(recommendations)} 条推荐", file=sys.stderr)

        # 处理JSON字段
        for rec in recommendations:
            if isinstance(rec['resources'], str):
                rec['resources'] = json.loads(rec['resources'])

        # 统计章节推荐和题目推荐
        chapter_recs = [rec for rec in recommendations if rec.get('chapterId')]
        problem_recs = [rec for rec in recommendations if rec.get('problemId')]

        print(f"包含 {len(chapter_recs)} 条章节推荐和 {len(problem_recs)} 条题目推荐", file=sys.stderr)

        # 打印章节推荐详情
        for rec in chapter_recs:
            print(f"章节推荐: {rec['title']} -> 章节ID: {rec['chapterId']}", file=sys.stderr)

        print(json.dumps({
            'success': True,
            'recommendations': recommendations
        }, cls=CustomJSONEncoder))
    except mysql.connector.Error as err:
        print(f"获取推荐失败: {str(err)}", file=sys.stderr)
        print(json.dumps({
            'success': False,
            'message': f"获取推荐失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def mark_as_read(student_id, recommendation_id):
    """标记推荐为已读"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 更新推荐状态
        cursor.execute("""
            UPDATE edu_learning_recommendations
            SET is_read = TRUE, read_at = NOW()
            WHERE id = %s AND student_id = %s
        """, (recommendation_id, student_id))

        if cursor.rowcount == 0:
            print(json.dumps({
                'success': False,
                'message': "未找到指定推荐或无权限修改"
            }))
            return

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "已标记为已读"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"标记已读失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': "参数不足"
        }))
        return

    command = sys.argv[1]

    if command == 'create_tables':
        create_tables()
    elif command == 'get_recommendations':
        if len(sys.argv) < 3:
            print(json.dumps({
                'success': False,
                'message': "缺少学生ID参数"
            }))
            return
        student_id = sys.argv[2]
        get_recommendations(student_id)
    elif command == 'mark_as_read':
        if len(sys.argv) < 4:
            print(json.dumps({
                'success': False,
                'message': "缺少必要参数"
            }))
            return
        student_id = sys.argv[2]
        recommendation_id = sys.argv[3]
        mark_as_read(student_id, recommendation_id)
    elif command == 'save_recommendations':
        if len(sys.argv) < 4:
            print(json.dumps({
                'success': False,
                'message': "缺少必要参数"
            }))
            return
        student_id = sys.argv[2]
        recommendations_json = sys.argv[3]
        try:
            recommendations = json.loads(recommendations_json)
            save_recommendations(student_id, recommendations)
        except json.JSONDecodeError:
            print(json.dumps({
                'success': False,
                'message': "推荐数据格式错误"
            }))
    else:
        print(json.dumps({
            'success': False,
            'message': f"未知命令: {command}"
        }))

if __name__ == "__main__":
    main()
