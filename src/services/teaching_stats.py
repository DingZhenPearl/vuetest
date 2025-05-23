import sys
import json
import mysql.connector
from datetime import datetime, date
from decimal import Decimal

# 使用与其他服务相同的数据库配置
from coding_data import DB_CONFIG

# 添加自定义JSON编码器
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

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

        # 首先检查是否有该班级的数据
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM edu_coding_submissions cs
            {where_clause}
        """, params)

        count_result = cursor.fetchone()
        has_data = count_result and count_result['count'] > 0

        if not has_data:
            print(f"警告: 没有找到班级 '{class_name}' 的数据", file=sys.stderr)

            # 返回空数据结构
            result = {
                'daily_trends': [],
                'problem_difficulty': [],
                'error_patterns': [],
                'progress_distribution': [],
                'efficiency_analysis': []
            }

            print(json.dumps({
                'success': True,
                'data': result,
                'message': f"没有找到班级 '{class_name}' 的数据"
            }, cls=CustomJSONEncoder))
            return

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

        daily_trends = cursor.fetchall() or []

        # 2. 分析问题难度分布
        # 使用edu_problem_solving_stats表中的time_spent_seconds字段计算平均解题时间
        # 这个字段记录了学生在解题过程中实际花费的时间（秒），更准确地反映了解题难度
        cursor.execute(f"""
            SELECT
                cs.problem_id,
                MAX(cs.problem_title) as problem_title,
                COUNT(*) as attempt_count,
                COUNT(DISTINCT cs.student_id) as student_count,
                SUM(CASE WHEN cs.submit_result = 'success' THEN 1 ELSE 0 END) / COUNT(*) * 100 as success_rate,
                AVG(CASE
                    WHEN ps.time_spent_seconds > 0
                    AND ps.time_spent_seconds <= 10800  -- 3小时 = 10800秒
                    THEN ps.time_spent_seconds  -- 直接使用秒数，不转换为分钟
                    ELSE NULL
                END) as avg_solution_time
            FROM edu_coding_submissions cs
            LEFT JOIN edu_problem_solving_stats ps ON cs.problem_id = ps.problem_id AND cs.student_id = ps.student_id
            {where_clause}
            GROUP BY cs.problem_id
            ORDER BY success_rate ASC
        """, params)

        problem_difficulty = cursor.fetchall() or []

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

        error_patterns = cursor.fetchall() or []

        # 4. 学习进度分布 - 修改查询以处理没有匹配记录的情况
        try:
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

            progress_distribution = cursor.fetchall() or []
        except mysql.connector.Error as err:
            print(f"获取学习进度分布失败: {str(err)}", file=sys.stderr)
            progress_distribution = []

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

        efficiency_analysis = cursor.fetchall() or []

        # 检查是否所有数据都为空
        all_empty = (
            len(daily_trends) == 0 and
            len(problem_difficulty) == 0 and
            len(error_patterns) == 0 and
            len(progress_distribution) == 0 and
            len(efficiency_analysis) == 0
        )

        if all_empty:
            print(f"警告: 所有查询都没有返回数据", file=sys.stderr)

        result = {
            'daily_trends': daily_trends,
            'problem_difficulty': problem_difficulty,
            'error_patterns': error_patterns,
            'progress_distribution': progress_distribution,
            'efficiency_analysis': efficiency_analysis
        }

        print(json.dumps({
            'success': True,
            'data': result,
            'message': '获取学习数据成功' if not all_empty else '没有找到有效的学习数据'
        }, cls=CustomJSONEncoder))  # 使用自定义编码器

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
    cursor = conn.cursor()

    try:
        # 从edu_coding_submissions表获取班级列表
        cursor.execute("""
            SELECT DISTINCT cs.student_class
            FROM edu_coding_submissions cs
            WHERE cs.student_class IS NOT NULL
            AND cs.student_class != ''
            AND cs.student_class != 'null'
        """)

        rows_from_submissions = cursor.fetchall()
        classes_from_submissions = [row[0] for row in rows_from_submissions if row[0]]

        # 从edu_profiles_student表获取班级列表
        cursor.execute("""
            SELECT DISTINCT class_name
            FROM edu_profiles_student
            WHERE class_name IS NOT NULL
            AND class_name != ''
            AND class_name != 'null'
        """)

        rows_from_profiles = cursor.fetchall()
        classes_from_profiles = [row[0] for row in rows_from_profiles if row[0]]

        # 合并两个来源的班级列表并去重
        all_classes = list(set(classes_from_submissions + classes_from_profiles))
        all_classes.sort()  # 确保稳定的排序

        if not all_classes:
            print(json.dumps({
                'success': True,
                'classes': [],
                'message': '暂无班级数据'
            }))
            return

        print(json.dumps({
            'success': True,
            'classes': all_classes,
            'message': '获取班级列表成功'
        }, cls=CustomJSONEncoder))
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
