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
    """创建用户个人信息表"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 创建学生个人信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_profiles_student (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                student_id VARCHAR(50),
                class_name VARCHAR(100),
                major VARCHAR(100),
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (email)
            )
        """)

        # 创建教师个人信息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edu_profiles_teacher (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                teacher_id VARCHAR(50),
                department VARCHAR(100),
                title VARCHAR(100),
                name VARCHAR(100),
                phone VARCHAR(20),
                office_location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX (email)
            )
        """)

        conn.commit()
        return True
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"创建表失败: {str(err)}"
        }))
        return False
    finally:
        cursor.close()
        conn.close()

def save_profile(email, student_id, class_name, major, name):
    """保存或更新用户个人信息"""
    # 确保表已创建
    if not create_tables():
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 检查是否已经存在该用户的记录
        cursor.execute("""
            SELECT id FROM edu_profiles_student WHERE email = %s
        """, (email,))

        result = cursor.fetchone()

        if result:
            # 更新现有记录
            cursor.execute("""
                UPDATE edu_profiles_student
                SET student_id = %s, class_name = %s, major = %s, name = %s
                WHERE email = %s
            """, (student_id, class_name, major, name, email))
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO edu_profiles_student (email, student_id, class_name, major, name)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, student_id, class_name, major, name))

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "个人信息保存成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"保存个人信息失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_profile(email):
    """获取用户个人信息"""
    # 确保表已创建
    if not create_tables():
        return

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT email, student_id, class_name, major, name,
                   created_at, updated_at
            FROM edu_profiles_student
            WHERE email = %s
        """, (email,))

        profile = cursor.fetchone()

        if profile:
            # 转换datetime对象为字符串
            profile['created_at'] = profile['created_at'].isoformat() if profile['created_at'] else None
            profile['updated_at'] = profile['updated_at'].isoformat() if profile['updated_at'] else None

            print(json.dumps({
                'success': True,
                'profile': profile
            }))
        else:
            print(json.dumps({
                'success': False,
                'message': "未找到该用户的个人信息"
            }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取个人信息失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def save_teacher_profile(email, teacher_id, department, title, name, phone, office_location):
    """保存或更新教师个人信息"""
    # 确保表已创建
    if not create_tables():
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 检查是否已经存在该教师的记录
        cursor.execute("""
            SELECT id FROM edu_profiles_teacher WHERE email = %s
        """, (email,))

        result = cursor.fetchone()

        if result:
            # 更新现有记录
            cursor.execute("""
                UPDATE edu_profiles_teacher
                SET teacher_id = %s, department = %s, title = %s, name = %s, phone = %s, office_location = %s
                WHERE email = %s
            """, (teacher_id, department, title, name, phone, office_location, email))
        else:
            # 创建新记录
            cursor.execute("""
                INSERT INTO edu_profiles_teacher (email, teacher_id, department, title, name, phone, office_location)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (email, teacher_id, department, title, name, phone, office_location))

        conn.commit()
        print(json.dumps({
            'success': True,
            'message': "教师个人信息保存成功"
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"保存教师个人信息失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_teacher_profile(email):
    """获取教师个人信息"""
    # 确保表已创建
    if not create_tables():
        return

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT email, teacher_id, department, title, name, phone, office_location,
                   created_at, updated_at
            FROM edu_profiles_teacher
            WHERE email = %s
        """, (email,))

        profile = cursor.fetchone()

        if profile:
            # 转换datetime对象为字符串
            profile['created_at'] = profile['created_at'].isoformat() if profile['created_at'] else None
            profile['updated_at'] = profile['updated_at'].isoformat() if profile['updated_at'] else None

            print(json.dumps({
                'success': True,
                'profile': profile
            }))
        else:
            print(json.dumps({
                'success': False,
                'message': "未找到该教师的个人信息"
            }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取教师个人信息失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_class_students(class_name):
    """获取班级所有学生"""
    # 确保表已创建
    if not create_tables():
        return

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT student_id, name, class_name, major, email
            FROM edu_profiles_student
            WHERE class_name = %s
        """, (class_name,))

        students = cursor.fetchall()

        # 转换datetime对象为字符串
        for student in students:
            if 'created_at' in student and student['created_at']:
                student['created_at'] = student['created_at'].isoformat()
            if 'updated_at' in student and student['updated_at']:
                student['updated_at'] = student['updated_at'].isoformat()

        print(json.dumps({
            'success': True,
            'students': students
        }))
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取班级学生失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': "缺少操作参数"
        }))
        sys.exit(1)

    operation = sys.argv[1]

    # 根据操作类型调用相应的函数
    if operation == "save_profile":
        if len(sys.argv) != 7:
            print(json.dumps({
                'success': False,
                'message': "参数不足，需要email, student_id, class_name, major, name"
            }))
            sys.exit(1)
        save_profile(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

    elif operation == "get_profile":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足，需要email"
            }))
            sys.exit(1)
        get_profile(sys.argv[2])

    elif operation == "get_class_students":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足，需要class_name"
            }))
            sys.exit(1)
        get_class_students(sys.argv[2])

    elif operation == "save_teacher_profile":
        if len(sys.argv) != 9:
            print(json.dumps({
                'success': False,
                'message': "参数不足，需要email, teacher_id, department, title, name, phone, office_location"
            }))
            sys.exit(1)
        save_teacher_profile(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8])

    elif operation == "get_teacher_profile":
        if len(sys.argv) != 3:
            print(json.dumps({
                'success': False,
                'message': "参数不足，需要email"
            }))
            sys.exit(1)
        get_teacher_profile(sys.argv[2])

    else:
        print(json.dumps({
            'success': False,
            'message': "未知的操作类型"
        }))
        sys.exit(1)