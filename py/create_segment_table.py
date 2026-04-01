#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：创建分段表
功能描述：执行SQL语句创建小说分段表
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

def create_segment_table(conn):
    """创建分段表"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 创建分段表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS segments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                novel_id INT NOT NULL COMMENT '小说ID',
                segment_number INT NOT NULL COMMENT '分段序号',
                content TEXT NOT NULL COMMENT '分段内容（约20字）',
                image_prompt TEXT COMMENT 'AI生成的图片提示词',
                image_url VARCHAR(500) COMMENT '生成的图片URL',
                is_processed BOOLEAN DEFAULT FALSE COMMENT '是否已处理',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                FOREIGN KEY (novel_id) REFERENCES novels(id) ON DELETE CASCADE,
                UNIQUE KEY idx_novel_segment (novel_id, segment_number),
                INDEX idx_novel_id (novel_id),
                INDEX idx_is_processed (is_processed)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='小说分段表'
        """)
        
        conn.commit()
        print("分段表创建成功！")
        return True
        
    except Exception as e:
        print(f"创建分段表失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始创建分段表...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 创建分段表
    if create_segment_table(conn):
        print("分段表创建完成！")
    else:
        print("分段表创建失败！")
    
    conn.close()

if __name__ == "__main__":
    main()