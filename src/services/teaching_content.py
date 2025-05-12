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
    """创建教学内容相关的数据表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建教学内容表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_teaching_contents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_email VARCHAR(255) NOT NULL,
                chapter_id VARCHAR(50) NOT NULL,
                chapter_number VARCHAR(50) NOT NULL,
                chapter_title VARCHAR(255) NOT NULL,
                chapter_difficulty ENUM('入门', '基础', '中级', '高级') NOT NULL,
                chapter_description TEXT NOT NULL,
                sections JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (teacher_email),
                INDEX (chapter_id)
            )
        """)

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "教学内容表创建成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"创建表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_all_chapters():
    """获取所有章节内容"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM edu_teaching_contents
            ORDER BY CAST(SUBSTRING(chapter_id, 3) AS UNSIGNED)
        """)

        chapters = cursor.fetchall()

        # 处理JSON字段
        for chapter in chapters:
            chapter['sections'] = json.loads(chapter['sections'])

        print(json.dumps({
            'success': True,
            'chapters': chapters
        }, cls=CustomJSONEncoder))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取章节失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_chapter(chapter_id):
    """获取指定章节内容"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT * FROM edu_teaching_contents
            WHERE chapter_id = %s
        """, (chapter_id,))

        chapter = cursor.fetchone()

        if chapter:
            chapter['sections'] = json.loads(chapter['sections'])
            print(json.dumps({
                'success': True,
                'chapter': chapter
            }, cls=CustomJSONEncoder))
        else:
            print(json.dumps({
                'success': False,
                'message': "章节不存在"
            }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取章节失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def add_chapter(data_json_str):
    """添加新章节"""
    try:
        data = json.loads(data_json_str)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 检查章节ID是否已存在
            cursor.execute("""
                SELECT id FROM edu_teaching_contents
                WHERE chapter_id = %s
            """, (data['chapter_id'],))

            if cursor.fetchone():
                print(json.dumps({
                    'success': False,
                    'message': "章节ID已存在"
                }))
                return

            # 插入新章节
            cursor.execute("""
                INSERT INTO edu_teaching_contents (
                    teacher_email, chapter_id, chapter_number, chapter_title,
                    chapter_difficulty, chapter_description, sections
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                data['teacher_email'],
                data['chapter_id'],
                data['chapter_number'],
                data['chapter_title'],
                data['chapter_difficulty'],
                data['chapter_description'],
                json.dumps(data['sections'])
            ))

            conn.commit()
            print(json.dumps({
                'success': True,
                'message': "章节添加成功",
                'chapter_id': data['chapter_id']
            }))
        except mysql.connector.Error as err:
            print(json.dumps({
                'success': False,
                'message': f"添加章节失败: {str(err)}"
            }))
        finally:
            cursor.close()
            conn.close()
    except json.JSONDecodeError:
        print(json.dumps({
            'success': False,
            'message': "无效的JSON数据"
        }))

def update_chapter(data_json_str):
    """更新章节内容"""
    try:
        data = json.loads(data_json_str)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # 检查章节是否存在
            cursor.execute("""
                SELECT id FROM edu_teaching_contents
                WHERE chapter_id = %s
            """, (data['chapter_id'],))

            if not cursor.fetchone():
                print(json.dumps({
                    'success': False,
                    'message': "章节不存在"
                }))
                return

            # 更新章节
            cursor.execute("""
                UPDATE edu_teaching_contents SET
                    chapter_number = %s,
                    chapter_title = %s,
                    chapter_difficulty = %s,
                    chapter_description = %s,
                    sections = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE chapter_id = %s
            """, (
                data['chapter_number'],
                data['chapter_title'],
                data['chapter_difficulty'],
                data['chapter_description'],
                json.dumps(data['sections']),
                data['chapter_id']
            ))

            conn.commit()
            print(json.dumps({
                'success': True,
                'message': "章节更新成功"
            }))
        except mysql.connector.Error as err:
            print(json.dumps({
                'success': False,
                'message': f"更新章节失败: {str(err)}"
            }))
        finally:
            cursor.close()
            conn.close()
    except json.JSONDecodeError:
        print(json.dumps({
            'success': False,
            'message': "无效的JSON数据"
        }))

def delete_chapter(chapter_id):
    """删除章节"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 检查章节是否存在
        cursor.execute("""
            SELECT id FROM edu_teaching_contents
            WHERE chapter_id = %s
        """, (chapter_id,))

        if not cursor.fetchone():
            print(json.dumps({
                'success': False,
                'message': "章节不存在"
            }))
            return

        # 删除章节
        cursor.execute("""
            DELETE FROM edu_teaching_contents
            WHERE chapter_id = %s
        """, (chapter_id,))

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "章节删除成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"删除章节失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': "缺少操作参数"
        }))
        sys.exit(1)

    operation = sys.argv[1]

    if operation == "create_tables":
        create_tables()
    elif operation == "get_all_chapters":
        get_all_chapters()
    elif operation == "get_chapter" and len(sys.argv) >= 3:
        get_chapter(sys.argv[2])
    elif operation == "add_chapter" and len(sys.argv) >= 3:
        add_chapter(sys.argv[2])
    elif operation == "update_chapter" and len(sys.argv) >= 3:
        update_chapter(sys.argv[2])
    elif operation == "delete_chapter" and len(sys.argv) >= 3:
        delete_chapter(sys.argv[2])
    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作或参数不足"
        }))
        sys.exit(1)
