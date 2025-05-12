#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import json
import sys
import argparse

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

def get_problems_by_chapter(chapter_id=None):
    """获取特定章节的题目，如果chapter_id为None则获取所有题目"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if chapter_id:
            cursor.execute("""
                SELECT id, title, difficulty, chapter_id
                FROM edu_problems
                WHERE chapter_id = %s
                ORDER BY id
            """, (chapter_id,))
        else:
            cursor.execute("""
                SELECT id, title, difficulty, chapter_id
                FROM edu_problems
                ORDER BY id
            """)
        
        problems = cursor.fetchall()
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
        
        if cursor.rowcount > 0:
            print(f"题目 {problem_id} 已关联到章节 {chapter_id}")
            return True
        else:
            print(f"题目 {problem_id} 不存在或未更新")
            return False
    except mysql.connector.Error as err:
        print(f"更新题目章节失败: {str(err)}")
        return False
    finally:
        cursor.close()
        conn.close()

def batch_update_by_difficulty():
    """根据题目难度批量更新章节关联"""
    chapters = get_all_chapters()
    if not chapters:
        print("没有找到章节数据")
        return
    
    # 显示章节列表
    print("\n可用章节列表:")
    for i, chapter in enumerate(chapters):
        print(f"{i+1}. {chapter['chapter_number']} {chapter['chapter_title']} (ID: {chapter['chapter_id']})")
    
    # 选择章节
    chapter_index = input("\n请选择要关联的章节编号 (1-7): ")
    if not chapter_index.strip() or not chapter_index.isdigit():
        print("无效的章节编号")
        return
    
    index = int(chapter_index) - 1
    if index < 0 or index >= len(chapters):
        print("无效的章节编号")
        return
    
    chapter_id = chapters[index]['chapter_id']
    print(f"已选择章节: {chapters[index]['chapter_number']} {chapters[index]['chapter_title']}")
    
    # 选择难度
    difficulty = input("\n请选择题目难度 (easy/medium/hard)，或输入'all'选择所有难度: ").lower()
    if difficulty not in ['easy', 'medium', 'hard', 'all']:
        print("无效的难度选择")
        return
    
    # 获取所有题目
    problems = get_problems_by_chapter()
    if not problems:
        print("没有找到题目数据")
        return
    
    # 筛选题目
    selected_problems = []
    for problem in problems:
        if difficulty == 'all' or problem['difficulty'] == difficulty:
            selected_problems.append(problem)
    
    if not selected_problems:
        print(f"没有找到难度为 {difficulty} 的题目")
        return
    
    # 显示选中的题目
    print(f"\n找到 {len(selected_problems)} 个{'所有难度' if difficulty == 'all' else difficulty}的题目:")
    for problem in selected_problems:
        current_chapter = "未关联" if problem['chapter_id'] is None else problem['chapter_id']
        print(f"ID: {problem['id']}, 标题: {problem['title']}, 当前章节: {current_chapter}")
    
    # 确认更新
    confirm = input(f"\n确认将这些题目关联到章节 {chapter_id}? (y/n): ").lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 批量更新
    success_count = 0
    for problem in selected_problems:
        if update_problem_chapter(problem['id'], chapter_id):
            success_count += 1
    
    print(f"\n成功更新 {success_count} 个题目的章节关联")

def main():
    parser = argparse.ArgumentParser(description='批量更新题目章节关联')
    parser.add_argument('--problem', type=int, help='题目ID')
    parser.add_argument('--chapter', type=str, help='章节ID')
    parser.add_argument('--list-chapters', action='store_true', help='列出所有章节')
    parser.add_argument('--list-problems', type=str, nargs='?', const='all', help='列出题目，可指定章节ID')
    
    args = parser.parse_args()
    
    if args.list_chapters:
        chapters = get_all_chapters()
        print("\n可用章节列表:")
        for chapter in chapters:
            print(f"{chapter['chapter_number']} {chapter['chapter_title']} (ID: {chapter['chapter_id']})")
    
    elif args.list_problems:
        chapter_id = None if args.list_problems == 'all' else args.list_problems
        problems = get_problems_by_chapter(chapter_id)
        
        if chapter_id:
            print(f"\n章节 {chapter_id} 的题目列表:")
        else:
            print("\n所有题目列表:")
        
        for problem in problems:
            current_chapter = "未关联" if problem['chapter_id'] is None else problem['chapter_id']
            print(f"ID: {problem['id']}, 标题: {problem['title']}, 难度: {problem['difficulty']}, 章节: {current_chapter}")
    
    elif args.problem and args.chapter:
        update_problem_chapter(args.problem, args.chapter)
    
    else:
        # 交互式模式
        batch_update_by_difficulty()

if __name__ == "__main__":
    main()
