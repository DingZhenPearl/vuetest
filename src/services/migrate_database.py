#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import json

# 源数据库配置
SOURCE_DBS = [
    {
        'host': 'localhost',
        'user': 'root',
        'password': 'sushiding',
        'database': 'user_auth_db'
    },
    {
        'host': 'localhost',
        'user': 'root',
        'password': 'sushiding',
        'database': 'chat_history'
    },
    {
        'host': 'localhost',
        'user': 'root',
        'password': 'sushiding',
        'database': 'my_database'
    }
]

# 目标数据库配置
TARGET_DB = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sushiding',
    'database': 'education_platform'
}

def create_target_database():
    """创建目标数据库"""
    conn = mysql.connector.connect(
        host=TARGET_DB['host'],
        user=TARGET_DB['user'],
        password=TARGET_DB['password']
    )
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TARGET_DB['database']}")
        print(f"目标数据库 {TARGET_DB['database']} 已创建或已存在")
    except Exception as e:
        print(f"创建目标数据库失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def migrate_tables():
    """迁移所有表到目标数据库"""
    # 先创建目标数据库
    create_target_database()
    
    # 从各源数据库迁移表结构和数据
    for source_db in SOURCE_DBS:
        try:
            # 连接源数据库
            source_conn = mysql.connector.connect(**source_db)
            source_cursor = source_conn.cursor()
            
            # 获取源数据库中的所有表
            source_cursor.execute("SHOW TABLES")
            tables = source_cursor.fetchall()
            
            if not tables:
                print(f"数据库 {source_db['database']} 中没有表")
                continue
                
            print(f"在 {source_db['database']} 中发现 {len(tables)} 个表")
            
            # 连接目标数据库
            target_conn = mysql.connector.connect(**TARGET_DB)
            target_cursor = target_conn.cursor()
            
            # 迁移每个表
            for table in tables:
                table_name = table[0]
                
                # 获取表结构
                source_cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table_stmt = source_cursor.fetchone()[1]
                
                try:
                    # 在目标数据库中创建表
                    target_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                    target_cursor.execute(create_table_stmt)
                    print(f"在目标数据库中创建表 {table_name}")
                    
                    # 获取数据
                    source_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = source_cursor.fetchall()
                    
                    if rows:
                        # 获取列名
                        source_cursor.execute(f"DESCRIBE {table_name}")
                        columns = source_cursor.fetchall()
                        column_names = [column[0] for column in columns]
                        placeholders = ", ".join(["%s"] * len(column_names))
                        columns_str = ", ".join(column_names)
                        
                        # 插入数据
                        for row in rows:
                            try:
                                target_cursor.execute(
                                    f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})", 
                                    row
                                )
                            except Exception as e:
                                print(f"插入数据到表 {table_name} 失败: {str(e)}")
                        
                        target_conn.commit()
                        print(f"从 {table_name} 迁移了 {len(rows)} 行数据")
                except Exception as e:
                    print(f"迁移表 {table_name} 失败: {str(e)}")
            
            source_cursor.close()
            source_conn.close()
            target_cursor.close()
            target_conn.close()
            
        except Exception as e:
            print(f"连接到数据库 {source_db['database']} 失败: {str(e)}")

if __name__ == "__main__":
    print("开始数据库迁移...")
    migrate_tables()
    print("数据库迁移完成")