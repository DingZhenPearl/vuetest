#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import mysql.connector
from datetime import datetime
import traceback

# 自定义JSON编码器，处理日期和Decimal类型
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        try:
            import decimal
            if isinstance(obj, decimal.Decimal):
                return float(obj)
        except ImportError:
            pass
        return super(CustomJSONEncoder, self).default(obj)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mwYgR7#*X2',
    'database': 'education_platform'
}

def save_section_progress(student_id, section_id):
    """保存学生完成小节的进度"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 检查记录是否已存在
        cursor.execute("""
            SELECT id FROM edu_section_progress
            WHERE student_id = %s AND section_id = %s
        """, (student_id, section_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新完成时间
            cursor.execute("""
                UPDATE edu_section_progress
                SET completed_at = CURRENT_TIMESTAMP
                WHERE student_id = %s AND section_id = %s
            """, (student_id, section_id))
        else:
            # 插入新记录
            cursor.execute("""
                INSERT INTO edu_section_progress (student_id, section_id)
                VALUES (%s, %s)
            """, (student_id, section_id))
        
        # 提交事务
        conn.commit()
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        # 返回结果
        print(json.dumps({
            'success': True,
            'message': '学习进度保存成功'
        }, cls=CustomJSONEncoder))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'保存学习进度失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def get_completed_sections(student_id):
    """获取学生已完成的小节列表"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 获取已完成的小节
        cursor.execute("""
            SELECT section_id, completed_at
            FROM edu_section_progress
            WHERE student_id = %s
            ORDER BY completed_at
        """, (student_id,))
        
        results = cursor.fetchall()
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        # 返回结果
        print(json.dumps({
            'success': True,
            'sections': results
        }, cls=CustomJSONEncoder))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'获取已完成小节失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

def import_from_localstorage(student_id, section_ids):
    """从localStorage导入学习进度数据"""
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 导入每个小节的进度
        for section_id in section_ids:
            # 检查记录是否已存在
            cursor.execute("""
                SELECT id FROM edu_section_progress
                WHERE student_id = %s AND section_id = %s
            """, (student_id, section_id))
            
            existing = cursor.fetchone()
            
            if not existing:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO edu_section_progress (student_id, section_id)
                    VALUES (%s, %s)
                """, (student_id, section_id))
        
        # 提交事务
        conn.commit()
        
        # 关闭数据库连接
        cursor.close()
        conn.close()
        
        # 返回结果
        print(json.dumps({
            'success': True,
            'message': f'成功导入 {len(section_ids)} 个已完成小节'
        }, cls=CustomJSONEncoder))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': f'导入学习进度数据失败: {str(e)}',
            'error': traceback.format_exc()
        }), file=sys.stderr)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'message': '缺少操作参数或学生ID'
        }), file=sys.stderr)
        sys.exit(1)

    operation = sys.argv[1]
    student_id = sys.argv[2]

    if operation == 'save_progress' and len(sys.argv) >= 4:
        section_id = sys.argv[3]
        save_section_progress(student_id, section_id)
    elif operation == 'get_completed':
        get_completed_sections(student_id)
    elif operation == 'import' and len(sys.argv) >= 4:
        section_ids = json.loads(sys.argv[3])
        import_from_localstorage(student_id, section_ids)
    else:
        print(json.dumps({
            'success': False,
            'message': f'未知操作: {operation} 或参数不足'
        }), file=sys.stderr)
