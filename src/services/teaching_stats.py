import sys
import json
import mysql.connector
from datetime import datetime, timedelta

# 使用与其他服务相同的数据库配置
from coding_data import DB_CONFIG

def get_db_connection():
    """建立数据库连接"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"数据库连接失败: {str(err)}"
        }))
        sys.exit(1)

def analyze_learning_patterns(class_name=None):
    """分析学习模式和趋势"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        where_clause = "WHERE 1=1"
        params = []
        if class_name:
            where_clause += " AND cs.student_class = %s"
            params.append(class_name)
            
        # 1. 分析每日提交趋势
        cursor.execute(f"""
            SELECT 
                DATE(submission_time) as date,
                COUNT(*) as total_submissions,
                COUNT(DISTINCT student_id) as active_students,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions
            FROM edu_coding_submissions cs
            {where_clause}
            GROUP BY DATE(submission_time)
            ORDER BY date DESC
            LIMIT 30
        """, params)
        
        daily_trends = cursor.fetchall()
        
        # 2. 分析问题难度分布
        cursor.execute(f"""
            SELECT 
                problem_id,
                MAX(problem_title) as problem_title,
                COUNT(*) as attempt_count,
                COUNT(DISTINCT student_id) as student_count,
                SUM(CASE WHEN submit_result = 'success' THEN 1 ELSE 0 END) / COUNT(*) * 100 as success_rate,
                AVG(TIMESTAMPDIFF(MINUTE, first_view_time, submission_time)) as avg_solution_time
            FROM edu_coding_submissions cs
            {where_clause}
            GROUP BY problem_id
            ORDER BY success_rate ASC
        """, params)
        
        problem_difficulty = cursor.fetchall()
        
        # 3. 分析常见错误模式
        cursor.execute(f"""
            SELECT 
                SUBSTRING_INDEX(execution_errors, '\n', 1) as error_type,
                COUNT(*) as occurrence_count,
                COUNT(DISTINCT student_id) as affected_students,
                GROUP_CONCAT(DISTINCT problem_id) as related_problems
            FROM edu_coding_submissions cs
            {where_clause} AND execution_errors IS NOT NULL
            GROUP BY error_type
            ORDER BY occurrence_count DESC
            LIMIT 10
        """, params)
        
        error_patterns = cursor.fetchall()
        
        # 4. 学习进度分布
        cursor.execute(f"""
            SELECT 
                ps.student_id,
                COUNT(DISTINCT ps.problem_id) as problems_attempted,
                SUM(ps.is_solved) as problems_solved,
                AVG(ps.attempts_until_success) as avg_attempts,
                AVG(ps.time_spent_seconds) as avg_time_spent
            FROM edu_problem_solving_stats ps
            JOIN edu_coding_submissions cs ON ps.student_id = cs.student_id
            {where_clause}
            GROUP BY ps.student_id
        """, params)
        
        progress_distribution = cursor.fetchall()
        
        # 5. 学习效率分析
        cursor.execute(f"""
            SELECT 
                cs.student_id,
                COUNT(*) as total_submissions,
                SUM(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) as successful_submissions,
                AVG(ps.time_spent_seconds) as avg_solving_time,
                MAX(ps.attempts_until_success) as max_attempts
            FROM edu_coding_submissions cs
            LEFT JOIN edu_problem_solving_stats ps 
                ON cs.student_id = ps.student_id AND cs.problem_id = ps.problem_id
            {where_clause}
            GROUP BY cs.student_id
        """, params)
        
        efficiency_analysis = cursor.fetchall()
        
        result = {
            'daily_trends': daily_trends,
            'problem_difficulty': problem_difficulty,
            'error_patterns': error_patterns,
            'progress_distribution': progress_distribution,
            'efficiency_analysis': efficiency_analysis
        }
        
        print(json.dumps({
            'success': True,
            'data': result
        }))
        
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"分析学习数据失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

def get_class_list():
    """获取所有班级列表"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT DISTINCT student_class
            FROM edu_coding_submissions
            WHERE student_class IS NOT NULL AND student_class != ''
            ORDER BY student_class
        """)
        
        class_list = cursor.fetchall()
        
        print(json.dumps({
            'success': True,
            'classes': [c['student_class'] for c in class_list]
        }))
        
    except mysql.connector.Error as err:
        print(json.dumps({
            'success': False,
            'message': f"获取班级列表失败: {str(err)}"
        }))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    operation = sys.argv[1] if len(sys.argv) > 1 else None
    
    if operation == "get_class_list":
        get_class_list()
    elif operation == "analyze_learning_patterns":
        class_name = sys.argv[2] if len(sys.argv) > 2 else None
        analyze_learning_patterns(class_name)
    else:
        print(json.dumps({
            'success': False,
            'message': "无效的操作"
        }))
