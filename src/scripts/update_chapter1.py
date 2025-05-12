#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# 第一章完整数据（包含所有视频内容）
CHAPTER1_DATA = {
    "id": "ch1",
    "number": "第一章",
    "title": "绪论",
    "difficulty": "入门",
    "description": "本章介绍数据结构的基本概念、算法分析方法以及时间复杂度和空间复杂度的基础知识。",
    "sections": [
        {
            "id": "ch1-s1",
            "title": "数据结构概述",
            "type": "theory",
            "duration": 15,
            "content": "<p>数据结构是计算机存储、组织数据的方式。数据结构是指相互之间存在一种或多种特定关系的数据元素的集合。</p><p>本节将介绍数据结构的基本概念和分类。</p>",
            "examples": [
                {
                    "title": "数据结构的分类",
                    "code": "线性结构：数组、链表、栈、队列\n非线性结构：树、图、堆\n文件结构：顺序文件、索引文件、散列文件",
                    "explanation": "这是数据结构的基本分类，不同的数据结构适用于不同的应用场景。"
                }
            ]
        },
        {
            "id": "ch1-s2",
            "title": "算法分析基础",
            "type": "theory",
            "duration": 20,
            "content": "<p>算法分析是指对一个算法所需的计算资源进行预测和度量。主要包括时间复杂度和空间复杂度的分析。</p>",
            "examples": [
                {
                    "title": "常见的时间复杂度",
                    "code": "O(1)    - 常数时间复杂度\nO(log n) - 对数时间复杂度\nO(n)    - 线性时间复杂度\nO(n log n) - 线性对数时间复杂度\nO(n²)   - 平方时间复杂度\nO(n³)   - 立方时间复杂度\nO(2ⁿ)   - 指数时间复杂度",
                    "explanation": "时间复杂度表示算法执行时间与数据规模之间的关系，O表示渐进上界。"
                }
            ]
        },
        {
            "id": "ch1-s3",
            "title": "算法效率分析",
            "type": "exercise",
            "duration": 25,
            "content": "<p>算法效率分析是评估算法性能的重要手段，通过分析算法的时间复杂度和空间复杂度来比较不同算法的优劣。</p>",
            "task": "分析以下代码片段的时间复杂度，并解释你的分析过程。",
            "template": "// 代码片段1\nfor (int i = 0; i < n; i++) {\n    sum += i;\n}\n\n// 代码片段2\nfor (int i = 0; i < n; i++) {\n    for (int j = 0; j < n; j++) {\n        sum += i * j;\n    }\n}"
        },
        {
            "id": "ch1-s4",
            "title": "数据结构基本认知与必要知识复习",
            "type": "video",
            "duration": 30,
            "videoUrl": "//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=1&high_quality=1&danmaku=0&as_wide=1",
            "content": "<p>本视频介绍了数据结构的基本概念和必要的预备知识，帮助你建立对数据结构的基本认知。</p><p>视频来源：<a href=\"https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383\" target=\"_blank\">数据结构与算法入门</a></p>"
        },
        {
            "id": "ch1-s5",
            "title": "指针_结构体_动态内存分配_算法时间复杂度",
            "type": "video",
            "duration": 30,
            "videoUrl": "//player.bilibili.com/player.html?bvid=BV1tNpbekEht&page=2&high_quality=1&danmaku=0&as_wide=1",
            "content": "<p>本视频介绍了数据结构实现所需的C++基础知识，包括指针、结构体、动态内存分配，以及算法时间复杂度的概念。</p><p>视频来源：<a href=\"https://www.bilibili.com/video/BV1tNpbekEht?spm_id_from=333.788.videopod.episodes&vd_source=b2db96ad408b1aec2d36beb0efe4d383&p=2\" target=\"_blank\">数据结构与算法入门</a></p>"
        },
        {
            "id": "ch1-s6",
            "title": "绪论知识测验",
            "type": "quiz",
            "duration": 10,
            "content": "<p>完成以下测验来测试你对数据结构绪论的理解。</p>",
            "questions": [
                {
                    "text": "以下哪种时间复杂度最高效？",
                    "options": ["O(n²)", "O(n log n)", "O(n)", "O(log n)"],
                    "correctAnswer": 3
                },
                {
                    "text": "数据结构主要研究的内容是什么？",
                    "options": ["数据的逻辑结构", "数据的物理结构", "数据的操作", "以上都是"],
                    "correctAnswer": 3
                },
                {
                    "text": "以下哪种不是线性数据结构？",
                    "options": ["数组", "链表", "树", "栈"],
                    "correctAnswer": 2
                }
            ]
        }
    ]
}

def update_chapter1():
    """更新第一章内容"""
    teacher_email = "teacher@example.com"
    
    print(f"正在更新章节: {CHAPTER1_DATA['title']}")
    
    # 准备章节数据
    chapter_data = {
        "teacher_email": teacher_email,
        "chapter_id": CHAPTER1_DATA["id"],
        "chapter_number": CHAPTER1_DATA["number"],
        "chapter_title": CHAPTER1_DATA["title"],
        "chapter_difficulty": CHAPTER1_DATA["difficulty"],
        "chapter_description": CHAPTER1_DATA["description"],
        "sections": CHAPTER1_DATA["sections"]
    }
    
    # 发送请求更新章节
    try:
        response = requests.put(
            f"http://localhost:3000/api/teaching-content/chapters/{CHAPTER1_DATA['id']}",
            json=chapter_data
        )
        
        result = response.json()
        
        if result.get("success"):
            print(f"章节 '{CHAPTER1_DATA['title']}' 更新成功")
        else:
            print(f"章节 '{CHAPTER1_DATA['title']}' 更新失败: {result.get('message')}")
    except Exception as e:
        print(f"更新章节失败: {str(e)}")

if __name__ == "__main__":
    update_chapter1()
