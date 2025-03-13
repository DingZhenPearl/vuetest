import mysql.connector
import json
import sys
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sushiding',
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
    """创建必要的数据表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建问题表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_problems (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_email VARCHAR(255) NOT NULL,
                title VARCHAR(255) NOT NULL,
                difficulty ENUM('easy', 'medium', 'hard') NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (teacher_email)
            )
        """)
        
        conn.commit()
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"创建表失败: {str(err)}"
        }))
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

def submit_problem(email, title, difficulty, content):
    """提交新题目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO edu_problems (teacher_email, title, difficulty, content)
            VALUES (%s, %s, %s, %s)
        """, (email, title, difficulty, content))
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "题目提交成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"提交题目失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_teacher_problems(email):
    """获取特定教师的题目列表"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, title, difficulty, content, created_at, updated_at
            FROM edu_problems
            WHERE teacher_email = %s
            ORDER BY created_at DESC
        """, (email,))
        
        problems = cursor.fetchall()
        
        # 转换时间戳为字符串，以便JSON序列化
        for p in problems:
            p['created_at'] = p['created_at'].isoformat()
            p['updated_at'] = p['updated_at'].isoformat()
        
        print(json.dumps({
            'success': True,
            'problems': problems
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取题目列表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def update_problem(problem_id, title, difficulty, content):
    """更新题目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE edu_problems 
            SET title = %s, difficulty = %s, content = %s
            WHERE id = %s
        """, (title, difficulty, content, problem_id))
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "题目更新成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"更新题目失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def delete_problem(problem_id):
    """删除题目"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM edu_problems WHERE id = %s
        """, (problem_id,))
        
        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "题目删除成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"删除题目失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_all_problems():
    """获取所有题目列表，供学生端使用"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT id, teacher_email, title, difficulty, content, created_at, updated_at
            FROM edu_problems
            ORDER BY created_at DESC
        """)
        
        problems = cursor.fetchall()
        
        # 转换时间戳为字符串，以便JSON序列化
        for p in problems:
            p['created_at'] = p['created_at'].isoformat()
            p['updated_at'] = p['updated_at'].isoformat()
        
        print(json.dumps({
            'success': True,
            'problems': problems
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取题目列表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 确保数据表存在
    create_tables()
    
    # 获取命令行参数
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': "缺少操作参数"
        }))
        sys.exit(1)
    
    operation = sys.argv[1]
    
    # 根据操作类型调用相应的函数
    if operation == "submit_problem":
        if len(sys.argv) != 6:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        submit_problem(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    elif operation == "get_teacher_problems":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        get_teacher_problems(sys.argv[2])
    
    elif operation == "update_problem":
        if len(sys.argv) != 6:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        update_problem(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    elif operation == "delete_problem":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        delete_problem(sys.argv[2])
    
    elif operation == "get_all_problems":
        get_all_problems()
    
    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作"
        }))