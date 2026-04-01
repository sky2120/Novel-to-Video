#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：添加图片URL字段到数据库表
功能描述：为characters、scenes、items表添加图片URL字段
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

def add_image_url_columns(conn):
    """添加图片URL字段"""
    cursor = conn.cursor()
    
    try:
        # 为角色表添加图片URL字段
        cursor.execute("""
            ALTER TABLE characters
            ADD COLUMN face_image_front VARCHAR(500) COMMENT '正面脸部图片URL',
            ADD COLUMN face_image_side VARCHAR(500) COMMENT '侧面脸部图片URL',
            ADD COLUMN face_image_half VARCHAR(500) COMMENT '半侧面脸部图片URL'
        """)
        print("已为characters表添加图片URL字段")
        
        # 为场景表添加图片URL字段
        cursor.execute("""
            ALTER TABLE scenes
            ADD COLUMN image_url VARCHAR(500) COMMENT '场景图片URL'
        """)
        print("已为scenes表添加图片URL字段")
        
        # 为物品表添加图片URL字段
        cursor.execute("""
            ALTER TABLE items
            ADD COLUMN image_url VARCHAR(500) COMMENT '物品图片URL'
        """)
        print("已为items表添加图片URL字段")
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"添加字段失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始添加图片URL字段到数据库表...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 添加字段
    success = add_image_url_columns(conn)
    
    conn.close()
    
    if success:
        print("图片URL字段添加成功！")
    else:
        print("图片URL字段添加失败！")

if __name__ == "__main__":
    main()