#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：创建新的数据表
功能描述：创建新的chapters和scene_segments表
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


def create_tables(conn):
    """创建数据表"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 创建chapters表
        print("正在创建chapters表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                novel_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                chapter_number INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        # 创建scene_segments表（每个分段对应一张图片）
        print("正在创建scene_segments表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scene_segments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                chapter_id INT NOT NULL,
                segment_number INT NOT NULL,
                content TEXT NOT NULL,
                image_prompt TEXT,
                image_url VARCHAR(500),
                is_processed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (chapter_id) REFERENCES chapters(id) ON DELETE CASCADE,
                UNIQUE KEY unique_segment (chapter_id, segment_number)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
        
        conn.commit()
        print("表创建成功！")
        return True
        
    except Exception as e:
        print(f"创建表失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def main():
    """主函数"""
    print("开始创建新的数据表...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 创建表
    if create_tables(conn):
        print("\n数据表创建完成！")
    else:
        print("\n数据表创建失败！")
    
    conn.close()


if __name__ == "__main__":
    main()
