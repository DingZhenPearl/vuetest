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
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP NULL,
                INDEX (student_id)
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
        # 先删除该学生未读的旧推荐
        cursor.execute("""
            DELETE FROM edu_learning_recommendations
            WHERE student_id = %s AND is_read = FALSE
        """, (student_id,))
        
        # 插入新推荐
        for rec in recommendations:
            cursor.execute("""
                INSERT INTO edu_learning_recommendations
                (student_id, title, description, priority, resources, actionable, problem_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                student_id,
                rec['title'],
                rec['description'],
                rec['priority'],
                json.dumps(rec.get('resources', [])),
                rec.get('actionable', False),
                rec.get('problemId')
            ))
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "推荐保存成功"
        }))
    except mysql.connector.Error as err:
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
        
        # 处理JSON字段
        for rec in recommendations:
            if isinstance(rec['resources'], str):
                rec['resources'] = json.loads(rec['resources'])
        
        print(json.dumps({
            'success': True,
            'recommendations': recommendations
        }, cls=CustomJSONEncoder))
    except mysql.connector.Error as err:
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
