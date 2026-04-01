#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：删除数据表
功能描述：删除现有的chapters和segments表
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


def drop_tables(conn):
    """删除数据表"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 删除segments表（先删除外键约束的表）
        print("正在删除segments表...")
        cursor.execute("DROP TABLE IF EXISTS segments")
        
        # 删除chapters表
        print("正在删除chapters表...")
        cursor.execute("DROP TABLE IF EXISTS chapters")
        
        conn.commit()
        print("表删除成功！")
        return True
        
    except Exception as e:
        print(f"删除表失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def main():
    """主函数"""
    print("开始删除数据表...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 删除表
    if drop_tables(conn):
        print("\n数据表删除完成！")
    else:
        print("\n数据表删除失败！")
    
    conn.close()


if __name__ == "__main__":
    main()
