#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：检查分段数据
功能描述：查看数据库中segments表的内容
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


def check_segments(conn):
    """检查分段数据"""
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 查询segments表
        cursor.execute("""
            SELECT s.id, s.chapter_id, s.segment_number, s.content, s.image_prompt, s.is_processed,
                   c.title as chapter_title
            FROM segments s
            JOIN chapters c ON s.chapter_id = c.id
            ORDER BY s.chapter_id, s.segment_number
        """)
        segments = cursor.fetchall()
        
        print(f"数据库中有 {len(segments)} 个分段")
        
        for segment_id, chapter_id, segment_number, content, image_prompt, is_processed, chapter_title in segments:
            print(f"\n分段ID: {segment_id}")
            print(f"章节: {chapter_title} (ID: {chapter_id})")
            print(f"分段序号: {segment_number}")
            print(f"内容: {content}")
            print(f"图片提示词: {image_prompt if image_prompt else '未生成'}")
            print(f"处理状态: {'已处理' if is_processed else '未处理'}")
            
    except Exception as e:
        print(f"查询分段数据失败: {e}")
    finally:
        cursor.close()


def main():
    """主函数"""
    print("开始检查分段数据...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 检查分段数据
    check_segments(conn)
    
    conn.close()


if __name__ == "__main__":
    main()
