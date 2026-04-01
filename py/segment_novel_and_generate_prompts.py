#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：小说分段和图片提示词生成
功能描述：将小说章节分成小段，调用AI生成图片提示词，保存到分段表中
作者：AI Assistant
日期：2026-03-31
"""

import os
import json
import pymysql
import requests
import re

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'


def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_api_key(config):
    """加载API密钥"""
    return config['api']['kimi_api_key']


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


def get_all_chapters(conn):
    """获取所有未处理的章节"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, novel_id, title, content 
            FROM chapters 
            WHERE id NOT IN (SELECT DISTINCT chapter_id FROM segments)
        """)
        chapters = cursor.fetchall()
        return chapters
    except Exception as e:
        print(f"获取章节信息失败: {e}")
        return []
    finally:
        cursor.close()


def segment_text(text, segment_length=20):
    """将文本分成指定长度的段落"""
    segments = []
    text = text.strip()
    
    # 去除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    i = 0
    while i < len(text):
        # 找到合适的分割点（尽量在句子结束处分割）
        end_pos = i + segment_length
        
        # 如果超过文本长度，直接取剩余部分
        if end_pos >= len(text):
            segment = text[i:]
            segments.append(segment)
            break
        
        # 尝试在句子结束符处分割
        for j in range(end_pos, max(i, end_pos - 10), -1):
            if text[j] in '。！？.!?':
                segment = text[i:j+1]
                segments.append(segment)
                i = j + 1
                break
        else:
            # 如果没有找到合适的分割点，强制分割
            segment = text[i:end_pos]
            segments.append(segment)
            i = end_pos
    
    return segments


def call_ai_api(api_key, segment_content):
    """调用AI生成图片提示词"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    prompt = f"""
请根据以下小说片段生成一个详细的图片提示词，用于AI图像生成：

小说片段：{segment_content}

要求：
1. 提示词要具体、详细，能够准确描述场景、人物、动作、氛围等视觉元素
2. 包含构图、光线、色彩、风格等艺术元素
3. 使用中文描述，不要包含任何标记或格式
4. 长度适中，适合AI图像生成

请直接返回提示词内容，不要添加任何额外说明。
    """
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"AI API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prompt = result['choices'][0]['message']['content'].strip()
            return prompt
        else:
            print(f"AI API调用失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"调用AI API失败: {e}")
        return None


def save_segments_to_db(conn, chapter_id, segments):
    """保存分段到数据库"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 批量插入分段
        insert_data = []
        for i, segment in enumerate(segments, 1):
            insert_data.append((chapter_id, i, segment))
        
        cursor.executemany("""
            INSERT INTO segments (chapter_id, segment_number, content)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE content = VALUES(content)
        """, insert_data)
        
        conn.commit()
        print(f"成功保存 {len(segments)} 个分段到数据库")
        return True
        
    except Exception as e:
        print(f"保存分段失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def generate_prompts_for_segments(conn, api_key):
    """为未处理的分段生成图片提示词"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 获取未处理的分段
        cursor.execute("""
            SELECT id, content 
            FROM segments 
            WHERE is_processed = FALSE
            LIMIT 100
        """)
        segments = cursor.fetchall()
        
        if not segments:
            print("没有未处理的分段")
            return True
        
        print(f"找到 {len(segments)} 个未处理的分段")
        
        # 为每个分段生成提示词
        for segment_id, content in segments:
            print(f"\n处理分段 ID={segment_id}")
            print(f"内容: {content}")
            
            # 调用AI生成提示词
            prompt = call_ai_api(api_key, content)
            
            if prompt:
                print(f"生成的提示词: {prompt}")
                
                # 更新数据库
                cursor.execute("""
                    UPDATE segments 
                    SET image_prompt = %s, is_processed = TRUE 
                    WHERE id = %s
                """, (prompt, segment_id))
                conn.commit()
            else:
                print("提示词生成失败")
        
        return True
        
    except Exception as e:
        print(f"生成提示词失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def main():
    """主函数"""
    print("开始小说分段和图片提示词生成...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key(config)
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 获取未处理的章节
    chapters = get_all_chapters(conn)
    if not chapters:
        print("没有未处理的章节")
        conn.close()
        return
    
    print(f"找到 {len(chapters)} 个未处理的章节")
    
    # 处理每个章节
    for chapter_id, novel_id, title, content in chapters:
        print(f"\n{'='*60}")
        print(f"处理章节: {title}")
        print(f"{'='*60}")
        
        # 分段处理章节内容
        segments = segment_text(content, segment_length=20)
        print(f"章节内容已分成 {len(segments)} 个小段")
        
        # 保存分段到数据库
        if save_segments_to_db(conn, chapter_id, segments):
            print("分段保存成功")
        else:
            print("分段保存失败")
    
    # 为分段生成图片提示词
    print("\n" + "="*60)
    print("开始为分段生成图片提示词...")
    print("="*60)
    
    if generate_prompts_for_segments(conn, api_key):
        print("提示词生成完成")
    else:
        print("提示词生成失败")
    
    conn.close()
    print("\n小说分段和图片提示词生成完成！")


if __name__ == "__main__":
    main()