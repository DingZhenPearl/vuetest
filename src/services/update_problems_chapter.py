#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import json
import sys

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

def alter_table():
    """修改edu_problems表，添加chapter_id字段"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'education_platform' 
            AND TABLE_NAME = 'edu_problems' 
            AND COLUMN_NAME = 'chapter_id'
        """)
        
        if cursor.fetchone()[0] == 0:
            # 字段不存在，添加字段
            cursor.execute("""
                ALTER TABLE edu_problems 
                ADD COLUMN chapter_id VARCHAR(50) NULL,
                ADD INDEX (chapter_id)
            """)
            
            print(json.dumps({
                'success': True,
                'message': "成功添加chapter_id字段"
            }))
        else:
            print(json.dumps({
                'success': True,
                'message': "chapter_id字段已存在"
            }))
        
        conn.commit()
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"修改表结构失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_all_chapters():
    """获取所有章节"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT chapter_id, chapter_number, chapter_title 
            FROM edu_teaching_contents
            ORDER BY CAST(SUBSTRING(chapter_id, 3) AS UNSIGNED)
        """)
        
        chapters = cursor.fetchall()
        
        print(json.dumps({
            'success': True,
            'chapters': chapters
        }))
        
        return chapters
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取章节失败: {str(err)}"
        }))
        return []
    finally:
        cursor.close()
        conn.close()

def get_all_problems():
    """获取所有题目"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, title, difficulty, chapter_id
            FROM edu_problems
            ORDER BY id
        """)
        
        problems = cursor.fetchall()
        
        print(json.dumps({
            'success': True,
            'problems': problems
        }))
        
        return problems
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取题目失败: {str(err)}"
        }))
        return []
    finally:
        cursor.close()
        conn.close()

def update_problem_chapter(problem_id, chapter_id):
    """更新题目的章节关联"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE edu_problems
            SET chapter_id = %s
            WHERE id = %s
        """, (chapter_id, problem_id))
        
        conn.commit()
        
        print(json.dumps({
            'success': True,
            'message': f"题目 {problem_id} 已关联到章节 {chapter_id}"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"更新题目章节失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def batch_update_problems(mapping):
    """批量更新题目的章节关联"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for problem_id, chapter_id in mapping.items():
            cursor.execute("""
                UPDATE edu_problems
                SET chapter_id = %s
                WHERE id = %s
            """, (chapter_id, problem_id))
        
        conn.commit()
        
        print(json.dumps({
            'success': True,
            'message': f"已批量更新 {len(mapping)} 个题目的章节关联"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"批量更新题目章节失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def interactive_mapping():
    """交互式为题目分配章节"""
    # 确保表结构正确
    alter_table()
    
    # 获取所有章节
    chapters = get_all_chapters()
    if not chapters:
        print("没有找到章节数据")
        return
    
    # 获取所有题目
    problems = get_all_problems()
    if not problems:
        print("没有找到题目数据")
        return
    
    # 显示章节列表
    print("\n可用章节列表:")
    for i, chapter in enumerate(chapters):
        print(f"{i+1}. {chapter['chapter_number']} {chapter['chapter_title']} (ID: {chapter['chapter_id']})")
    
    # 为每个题目选择章节
    mapping = {}
    for problem in problems:
        if problem['chapter_id']:
            print(f"\n题目 {problem['id']}: {problem['title']} 已关联到章节 {problem['chapter_id']}")
            change = input("是否修改关联? (y/n): ").lower()
            if change != 'y':
                continue
        
        print(f"\n题目 {problem['id']}: {problem['title']} (难度: {problem['difficulty']})")
        chapter_index = input(f"请选择关联章节编号 (1-{len(chapters)})，或按Enter跳过: ")
        
        if chapter_index.strip() and chapter_index.isdigit():
            index = int(chapter_index) - 1
            if 0 <= index < len(chapters):
                chapter_id = chapters[index]['chapter_id']
                mapping[problem['id']] = chapter_id
                print(f"已选择章节: {chapters[index]['chapter_number']} {chapters[index]['chapter_title']}")
    
    # 批量更新
    if mapping:
        print(f"\n将更新 {len(mapping)} 个题目的章节关联")
        confirm = input("确认更新? (y/n): ").lower()
        if confirm == 'y':
            batch_update_problems(mapping)
    else:
        print("\n没有需要更新的题目")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        operation = sys.argv[1]
        
        if operation == "alter_table":
            alter_table()
        elif operation == "get_chapters":
            get_all_chapters()
        elif operation == "get_problems":
            get_all_problems()
        elif operation == "update" and len(sys.argv) == 4:
            update_problem_chapter(sys.argv[2], sys.argv[3])
        else:
            print(json.dumps({
                'success': False,
                'message': "无效的操作或参数不足"
            }))
    else:
        # 交互式模式
        interactive_mapping()
