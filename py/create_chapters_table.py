#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：创建章节表
功能描述：执行SQL语句创建小说章节表
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

def create_chapters_table(conn):
    """创建章节表"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 创建章节表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INT AUTO_INCREMENT PRIMARY KEY,
                novel_id INT NOT NULL COMMENT '小说ID',
                title VARCHAR(255) NOT NULL COMMENT '章节标题',
                content TEXT NOT NULL COMMENT '章节内容',
                chapter_number INT COMMENT '章节序号',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                UNIQUE KEY idx_novel_chapter (novel_id, title),
                INDEX idx_novel_id (novel_id),
                INDEX idx_chapter_number (chapter_number)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说章节表'
        """)
        
        conn.commit()
        print("章节表创建成功！")
        return True
        
    except Exception as e:
        print(f"创建章节表失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始创建章节表...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 创建章节表
    if create_chapters_table(conn):
        print("章节表创建完成！")
    else:
        print("章节表创建失败！")
    
    conn.close()

if __name__ == "__main__":
    main()