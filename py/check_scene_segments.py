#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：检查场景分段数据
功能描述：查看数据库中scene_segments表的内容
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


def check_scene_segments(conn):
    """检查场景分段数据"""
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 查询scene_segments表
        cursor.execute("""
            SELECT s.id, s.chapter_id, s.segment_number, s.content, s.image_prompt, s.is_processed,
                   c.title as chapter_title, n.title as novel_title
            FROM scene_segments s
            JOIN chapters c ON s.chapter_id = c.id
            JOIN novels n ON c.novel_id = n.id
            ORDER BY n.id, c.chapter_number, s.segment_number
        """)
        segments = cursor.fetchall()
        
        print(f"数据库中有 {len(segments)} 个场景分段")
        
        current_novel = None
        current_chapter = None
        
        for segment_id, chapter_id, segment_number, content, image_prompt, is_processed, chapter_title, novel_title in segments:
            # 打印小说标题（只在切换小说时打印）
            if novel_title != current_novel:
                current_novel = novel_title
                print(f"\n{'='*60}")
                print(f"小说: {novel_title}")
                print(f"{'='*60}")
            
            # 打印章节标题（只在切换章节时打印）
            if chapter_title != current_chapter:
                current_chapter = chapter_title
                print(f"\n章节: {chapter_title}")
            
            print(f"\n分段 {segment_number}:")
            print(f"内容: {content}")
            print(f"图片提示词: {image_prompt if image_prompt else '未生成'}")
            print(f"处理状态: {'已处理' if is_processed else '未处理'}")
            print(f"-" * 40)
            
    except Exception as e:
        print(f"查询分段数据失败: {e}")
    finally:
        cursor.close()


def main():
    """主函数"""
    print("开始检查场景分段数据...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 检查分段数据
    check_scene_segments(conn)
    
    conn.close()


if __name__ == "__main__":
    main()
