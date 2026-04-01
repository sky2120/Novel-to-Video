#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：检查小说数据
功能描述：查看数据库中novels表的内容
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

def check_novels(conn):
    """检查小说数据"""
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 查询novels表
        cursor.execute("SELECT id, title, style_prompt FROM novels")
        novels = cursor.fetchall()
        
        print(f"数据库中有 {len(novels)} 本小说")
        
        for novel_id, title, style_prompt in novels:
            print(f"\n小说ID: {novel_id}")
            print(f"标题: {title}")
            print(f"风格提示词: {style_prompt[:200]}..." if style_prompt else "风格提示词: 无")
            
    except Exception as e:
        print(f"查询小说数据失败: {e}")
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始检查小说数据...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 检查小说数据
    check_novels(conn)
    
    conn.close()

if __name__ == "__main__":
    main()