#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：检查数据库表结构
功能描述：查看数据库中的所有表结构
作者：AI Assistant
日期：2026-03-31
"""

import json
import pymysql

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def connect_db(config):
    """连接数据库"""
    try:
        conn = pymysql.connect(
            host=config['database']['host'],
            port=config['database']['port'],
            user=config['database']['user'],
            password=config['database']['password'],
            database=config['database']['database'],
            charset=config['database']['charset']
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def check_tables(conn):
    """检查数据库中的表"""
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 获取所有表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查chapters表是否存在
        has_chapters = False
        for table in tables:
            if table[0] == 'chapters':
                has_chapters = True
                break
        
        if has_chapters:
            print("\nchapters表结构:")
            cursor.execute("DESCRIBE chapters")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  {column[0]} - {column[1]}")
        else:
            print("\nchapters表不存在！")
            
    except Exception as e:
        print(f"检查表结构失败: {e}")
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始检查数据库表结构...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 检查表结构
    check_tables(conn)
    
    conn.close()

if __name__ == "__main__":
    main()