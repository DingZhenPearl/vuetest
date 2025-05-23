import mysql.connector
import json
import sys
from datetime import datetime

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
                input_example TEXT,
                output_example TEXT,
                chapter_id VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (teacher_email),
                INDEX (chapter_id)
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

def submit_problem(email, title, difficulty, content, input_example, output_example, chapter_id=None):
    """提交新题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO edu_problems (teacher_email, title, difficulty, content, input_example, output_example, chapter_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (email, title, difficulty, content, input_example, output_example, chapter_id))

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
    """获取题目列表(包括其他教师共享的题目)"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.id,
                p.title,
                p.difficulty,
                p.content,
                p.input_example,
                p.output_example,
                p.chapter_id,
                p.created_at,
                p.updated_at,
                p.teacher_email,
                CASE WHEN p.teacher_email = %s THEN 1 ELSE 0 END as is_owner
            FROM edu_problems p
            ORDER BY p.created_at DESC
        """, (email,))

        problems = cursor.fetchall()

        # 转换时间戳为字符串
        for p in problems:
            p['created_at'] = p['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            p['updated_at'] = p['updated_at'].strftime('%Y-%m-%d %H:%M:%S')

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

def update_problem(problem_id, title, difficulty, content, input_example, output_example, chapter_id=None):
    """更新题目"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE edu_problems
            SET title = %s, difficulty = %s, content = %s, input_example = %s, output_example = %s, chapter_id = %s
            WHERE id = %s
        """, (title, difficulty, content, input_example, output_example, chapter_id, problem_id))

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
            SELECT id, teacher_email, title, difficulty, content, input_example, output_example, chapter_id, created_at, updated_at
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

def get_problem_detail(problem_id):
    """获取单个题目的详细信息"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, teacher_email, title, difficulty, content, input_example, output_example, chapter_id, created_at, updated_at
            FROM edu_problems
            WHERE id = %s
        """, (problem_id,))

        problem = cursor.fetchone()

        if not problem:
            print(json.dumps({
                'success': False,
                'message': "题目不存在"
            }))
            return

        # 转换时间戳为字符串，以便JSON序列化
        problem['created_at'] = problem['created_at'].isoformat()
        problem['updated_at'] = problem['updated_at'].isoformat()

        print(json.dumps({
            'success': True,
            'problem': problem
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取题目详情失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_problem_submissions_stats(problem_id):
    """获取题目的答题情况统计"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                s.student_id,
                s.student_class,
                MAX(s.submit_result) as best_result,
                COUNT(*) as submission_count,
                MIN(s.submission_time) as first_submission,
                MAX(s.submission_time) as last_submission
            FROM edu_coding_submissions s
            WHERE s.problem_id = %s
            GROUP BY s.student_id, s.student_class
            ORDER BY s.student_class, s.student_id
        """, (problem_id,))

        submissions = cursor.fetchall()

        # 转换时间戳为字符串
        for sub in submissions:
            if sub['first_submission']:
                sub['first_submission'] = sub['first_submission'].strftime('%Y-%m-%d %H:%M:%S')
            if sub['last_submission']:
                sub['last_submission'] = sub['last_submission'].strftime('%Y-%m-%d %H:%M:%S')

        print(json.dumps({
            'success': True,
            'submissions': submissions
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取答题情况失败: {str(err)}"
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
        if len(sys.argv) < 8:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        # 检查是否提供了章节ID参数
        chapter_id = sys.argv[8] if len(sys.argv) >= 9 else None
        submit_problem(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], chapter_id)

    elif operation == "get_teacher_problems":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        get_teacher_problems(sys.argv[2])

    elif operation == "update_problem":
        if len(sys.argv) < 8:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        # 检查是否提供了章节ID参数
        chapter_id = sys.argv[8] if len(sys.argv) >= 9 else None
        update_problem(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], chapter_id)

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

    elif operation == "get_problem_detail":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        get_problem_detail(sys.argv[2])

    elif operation == "get_problem_submissions_stats":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足"
            }))
            sys.exit(1)
        get_problem_submissions_stats(sys.argv[2])

    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作"
        }))