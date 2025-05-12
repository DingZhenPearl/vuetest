#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import re

# 章节ID到章节号的映射
CHAPTER_NUMBER_MAP = {
    'ch1': '第一章',
    'ch2': '第二章',
    'ch3': '第三章',
    'ch4': '第四章',
    'ch5': '第五章',
    'ch6': '第六章',
    'ch7': '第七章',
    'ch8': '第八章',
    'ch9': '第九章',
    'ch10': '第十章',
    'ch11': '第十一章',
    'ch12': '第十二章',
    'ch13': '第十三章',
    'ch14': '第十四章',
    'ch15': '第十五章'
}

def fix_chapter_numbers():
    """修复章节号格式"""
    try:
        # 获取所有章节
        response = requests.get("http://localhost:3000/api/teaching-content/chapters")
        result = response.json()
        
        if not result.get("success"):
            print(f"获取章节失败: {result.get('message')}")
            return
        
        chapters = result.get("chapters", [])
        
        # 检查并更新每个章节的章节号
        for chapter in chapters:
            chapter_id = chapter.get('chapter_id')
            current_number = chapter.get('chapter_number')
            
            # 根据章节ID确定正确的章节号
            correct_number = CHAPTER_NUMBER_MAP.get(chapter_id)
            
            if not correct_number:
                # 如果没有预定义的映射，尝试从章节ID中提取数字
                match = re.search(r'ch(\d+)', chapter_id)
                if match:
                    num = int(match.group(1))
                    # 将数字转换为中文章节号
                    if 1 <= num <= 15:
                        correct_number = CHAPTER_NUMBER_MAP.get(f'ch{num}')
                    else:
                        correct_number = f"第{num}章"
                else:
                    print(f"无法确定章节 {chapter_id} 的正确章节号，跳过")
                    continue
            
            # 如果当前章节号不正确，更新它
            if current_number != correct_number:
                print(f"更新章节 {chapter_id} 的章节号: {current_number} -> {correct_number}")
                
                # 准备更新数据
                update_data = {
                    "teacher_email": chapter.get('teacher_email'),
                    "chapter_id": chapter_id,
                    "chapter_number": correct_number,
                    "chapter_title": chapter.get('chapter_title'),
                    "chapter_difficulty": chapter.get('chapter_difficulty'),
                    "chapter_description": chapter.get('chapter_description'),
                    "sections": chapter.get('sections')
                }
                
                # 发送更新请求
                update_response = requests.put(
                    f"http://localhost:3000/api/teaching-content/chapters/{chapter_id}",
                    json=update_data
                )
                
                update_result = update_response.json()
                
                if update_result.get("success"):
                    print(f"章节 {chapter_id} 更新成功")
                else:
                    print(f"章节 {chapter_id} 更新失败: {update_result.get('message')}")
            else:
                print(f"章节 {chapter_id} 的章节号已正确: {current_number}")
        
        print("章节号修复完成")
    
    except Exception as e:
        print(f"修复章节号失败: {str(e)}")

if __name__ == "__main__":
    fix_chapter_numbers()
