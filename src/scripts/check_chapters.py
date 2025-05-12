#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

def check_chapters():
    """检查章节内容"""
    try:
        # 获取所有章节
        response = requests.get("http://localhost:3000/api/teaching-content/chapters")
        result = response.json()
        
        if not result.get("success"):
            print(f"获取章节失败: {result.get('message')}")
            return
        
        chapters = result.get("chapters", [])
        
        # 检查每个章节的视频内容
        for chapter in chapters:
            print(f"\n章节: {chapter['chapter_title']} ({chapter['chapter_id']})")
            
            sections = chapter.get("sections", [])
            video_sections = [s for s in sections if s.get("type") == "video"]
            
            if not video_sections:
                print("  没有视频内容")
            else:
                print(f"  包含 {len(video_sections)} 个视频小节:")
                for video in video_sections:
                    print(f"  - {video.get('title')} (URL: {video.get('videoUrl', '无URL')})")
    
    except Exception as e:
        print(f"检查章节失败: {str(e)}")

if __name__ == "__main__":
    check_chapters()
