#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：只生成图片提示词
功能描述：为已存在的分段生成图片提示词
作者：AI Assistant
日期：2026-03-31
"""

import json
import pymysql
import requests

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
    print("开始为分段生成图片提示词...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key(config)
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 为分段生成图片提示词
    if generate_prompts_for_segments(conn, api_key):
        print("\n提示词生成完成！")
    else:
        print("\n提示词生成失败！")
    
    conn.close()


if __name__ == "__main__":
    main()
