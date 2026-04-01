#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：导入小说章节到数据库
功能描述：将小说章节内容导入到chapters表中，并使用AI进行智能分段
作者：AI Assistant
日期：2026-03-31
"""

import os
import json
import pymysql
import requests

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'
NOVEL_DIR = 'novel'

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


def call_ai_segmentation(api_key, chapter_content):
    """调用AI进行智能分段"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""
请将以下小说章节内容按照场景进行智能分段。每个分段应该是一个完整的场景，可以在5秒视频中清晰展示。要求：

1. 每个分段必须是完整的语义单元，不能切割句子
2. 每个分段要简短，控制在80-120个中文字符以内，适合快速阅读
3. 分段要保持故事的连贯性和顺序性
4. 每个分段应该包含足够的信息来描述一个完整的画面
5. 返回格式：使用数字序号列出每个分段，每个分段占一行

小说章节内容：
{chapter_content}

请直接返回分段结果，不要添加任何额外说明。
    """
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"AI分段API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            segments_text = result['choices'][0]['message']['content'].strip()
            
            # 解析分段结果
            segments = []
            lines = segments_text.split('\n')
            
            for line in lines:
                line = line.strip()
                # 改进的解析逻辑：匹配任何数字开头的行
                if line:
                    # 检查是否以数字开头（如 "1. ", "2. ", "3. "等）
                    import re
                    match = re.match(r'^\d+\.\s*(.*)', line)
                    if match:
                        segment_content = match.group(1).strip()
                        if segment_content:
                            segments.append(segment_content)
                    elif len(segments) == 0:
                        # 如果还没有找到任何分段，且内容不为空，直接添加
                        # 这处理AI可能返回的特殊格式
                        segments.append(line)
            
            return segments
        else:
            print(f"AI分段API调用失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"调用AI分段API失败: {e}")
        return None

def get_novel_id(conn, novel_title):
    """获取小说ID"""
    if not conn:
        return None
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM novels WHERE title = %s", (novel_title,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    finally:
        cursor.close()

def import_chapters(conn, config):
    """导入章节到数据库并使用AI进行智能分段"""
    if not conn:
        return False, False
    
    cursor = conn.cursor()
    
    try:
        # 获取所有小说文件夹
        if not os.path.exists(NOVEL_DIR):
            print(f"目录不存在: {NOVEL_DIR}")
            return False, False
        
        novel_folders = []
        for item in os.listdir(NOVEL_DIR):
            item_path = os.path.join(NOVEL_DIR, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                novel_folders.append(item)
        
        if not novel_folders:
            print("没有找到小说文件夹")
            return False, False
        
        print(f"找到 {len(novel_folders)} 个小说文件夹")
        
        # 获取API密钥
        api_key = config['api']['kimi_api_key']
        
        chapters_imported = False
        all_segments_success = True
        
        for novel_folder_name in novel_folders:
            print(f"\n处理小说文件夹: {novel_folder_name}")
            
            # 从数据库获取小说ID
            cursor.execute("SELECT id FROM novels WHERE title = %s", (novel_folder_name,))
            result = cursor.fetchone()
            
            if not result:
                print(f"数据库中未找到小说: {novel_folder_name}，跳过处理")
                continue
            
            novel_id = result[0]
            print(f"获取到小说ID: {novel_id}")
            
            # 获取小说文件夹路径
            novel_folder_path = os.path.join(NOVEL_DIR, novel_folder_name)
            
            # 获取文件夹下的所有txt文件
            chapter_files = []
            for file in os.listdir(novel_folder_path):
                if file.endswith('.txt') and not file.startswith('.'):
                    chapter_files.append(file)
            
            if not chapter_files:
                print(f"小说文件夹中未找到章节文件: {novel_folder_name}")
                continue
            
            # 按文件名排序
            chapter_files.sort()
            print(f"找到 {len(chapter_files)} 个章节文件")
            
            # 获取已存在的章节
            cursor.execute("SELECT chapter_number FROM chapters WHERE novel_id = %s", (novel_id,))
            existing_chapters = set(row[0] for row in cursor.fetchall())
            
            # 插入章节到数据库并进行AI分段
            for i, chapter_file in enumerate(chapter_files, 1):
                try:
                    # 章节标题就是文件名（去掉.txt后缀）
                    chapter_title = os.path.splitext(chapter_file)[0]
                    chapter_file_path = os.path.join(novel_folder_path, chapter_file)
                    
                    # 读取章节内容（无论章节是否已存在）
                    with open(chapter_file_path, 'r', encoding='utf-8') as f:
                        chapter_content = f.read()
                    
                    if i in existing_chapters:
                        print(f"章节 {i} '{chapter_title}' 已存在，获取章节ID...")
                        # 查询已存在章节的ID
                        cursor.execute("SELECT id FROM chapters WHERE novel_id = %s AND chapter_number = %s", 
                                     (novel_id, i))
                        result = cursor.fetchone()
                        if result:
                            chapter_id = result[0]
                            print(f"章节ID: {chapter_id}")
                            chapters_imported = True
                        else:
                            print(f"未找到章节 {i} '{chapter_title}'，跳过处理")
                            continue
                    else:
                        # 插入章节
                        cursor.execute("""
                            INSERT INTO chapters (novel_id, title, content, chapter_number)
                            VALUES (%s, %s, %s, %s)
                        """, (novel_id, chapter_title, chapter_content, i))
                        
                        # 获取刚插入的章节ID
                        chapter_id = cursor.lastrowid
                        print(f"导入章节: {chapter_title} (ID: {chapter_id}, 序号: {i})")
                        chapters_imported = True
                    
                    # 调用AI进行智能分段
                    print(f"正在使用AI对章节 '{chapter_title}' 进行分段...")
                    segments = call_ai_segmentation(api_key, chapter_content)
                    
                    if segments:
                        print(f"AI成功将章节分成 {len(segments)} 个场景分段")
                        
                        # 保存分段到数据库
                        for j, segment_content in enumerate(segments, 1):
                            cursor.execute("""
                                INSERT INTO scene_segments (chapter_id, segment_number, content)
                                VALUES (%s, %s, %s)
                                ON DUPLICATE KEY UPDATE content = VALUES(content)
                            """, (chapter_id, j, segment_content))
                        print(f"成功保存 {len(segments)} 个分段到数据库")
                    else:
                        print("AI分段失败，跳过该章节的分段处理")
                        print("提示：请确保config.json中的API密钥是有效的moonshot API密钥（以sk-开头）")
                        all_segments_success = False
                        
                except Exception as e:
                    print(f"处理章节失败: {chapter_title}, 错误: {e}")
                    all_segments_success = False
            
            conn.commit()
            print(f"小说 {novel_folder_name} 的章节导入和分段完成")
        
        return chapters_imported, all_segments_success
        
    except Exception as e:
        print(f"导入章节失败: {e}")
        conn.rollback()
        return False, False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始导入小说章节到数据库...")
    
    # 加载配置
    config = load_config()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        print("\n" + "="*60)
        print("❌ 程序执行失败")
        print("未完成：数据库连接失败")
        print("="*60)
        return
    
    # 导入章节
    chapters_success, segments_success = import_chapters(conn, config)
    
    conn.close()
    
    print("\n" + "="*60)
    if chapters_success:
        print("✅ 程序执行完成")
        print("已完成：章节导入")
        if segments_success:
            print("已完成：所有章节的AI分段处理")
        else:
            print("未完成：部分章节的AI分段处理失败")
    else:
        print("❌ 程序执行失败")
        print("未完成：章节导入失败")
    
    print("="*60)

if __name__ == "__main__":
    main()