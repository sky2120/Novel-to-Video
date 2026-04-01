"""
程序名称：生成场景分段提示词
功能描述：读取数据库中的scene_segments表内容，调用文本对话AI生成图片提示词，保存到数据库
作者：AI Assistant
日期：2026-04-01
"""
import os
import json
import pymysql
import requests
import time

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_kimi_api_key(config):
    """加载文本对话API密钥"""
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

def get_all_segments(conn):
    """获取所有未生成提示词的场景分段"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, content FROM scene_segments 
            WHERE image_prompt IS NULL OR image_prompt = ''
            ORDER BY id ASC
        """)
        segments = cursor.fetchall()
        return segments
    except Exception as e:
        print(f"获取场景分段信息失败: {e}")
        return []
    finally:
        cursor.close()

def get_all_characters(conn):
    """获取所有人物信息"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT name, age, gender, personality, identity, hairstyle, face_shape, eyes, 
                   eyebrows, nose_mouth, skin_color, height_atmosphere, body_type, temperament, 
                   clothing_style, color_scheme, signature_decoration, art_style
            FROM characters
        """)
        characters = cursor.fetchall()
        return characters
    except Exception as e:
        print(f"获取人物信息失败: {e}")
        return []
    finally:
        cursor.close()

def extract_character_names(content, characters):
    """从文本中提取出现的人物名字"""
    character_names = []
    for char_info in characters:
        name = char_info[0]
        if name and name in content:
            character_names.append((name, char_info))
    return character_names

def generate_prompt_by_ai(api_key, content, characters_in_scene=None):
    """调用AI生成图片提示词"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 构建人物形象描述
    character_desc = ""
    if characters_in_scene:
        character_desc = "\n【人物形象】\n"
        for name, char_info in characters_in_scene:
            (name, age, gender, personality, identity, hairstyle, face_shape, eyes, 
             eyebrows, nose_mouth, skin_color, height_atmosphere, body_type, temperament, 
             clothing_style, color_scheme, signature_decoration, art_style) = char_info
            
            char_details = f"- {name}"
            if gender:
                char_details += f"，性别：{gender}"
            if age:
                char_details += f"，年龄：{age}岁"
            if hairstyle:
                char_details += f"，发型：{hairstyle}"
            if face_shape:
                char_details += f"，脸型：{face_shape}"
            if eyes:
                char_details += f"，眼睛：{eyes}"
            if clothing_style:
                char_details += f"，服装：{clothing_style}"
            if color_scheme:
                char_details += f"，配色：{color_scheme}"
            if signature_decoration:
                char_details += f"，装饰：{signature_decoration}"
            
            character_desc += char_details + "\n"
    
    prompt = f"""请根据以下小说场景内容，生成一个详细的图片提示词。要求：

1. 提示词要详细描述场景的视觉元素，包括人物、环境、氛围等
2. 如果场景中有人物，请使用提供的人物形象描述
3. 提示词要适合用于AI图像生成，包含足够的细节
4. 语言风格要符合国漫风格
5. 只返回提示词，不要添加其他说明文字

【场景内容】
{content}

{character_desc}

请直接返回图片提示词："""
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"AI提示词生成响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            prompt_text = result['choices'][0]['message']['content'].strip()
            return prompt_text
        else:
            print(f"AI提示词生成失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"调用AI提示词生成失败: {e}")
        return None

def update_segment_prompt(conn, segment_id, prompt):
    """更新场景分段提示词到数据库"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scene_segments 
            SET image_prompt = %s 
            WHERE id = %s
        """, (prompt, segment_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新场景分段提示词失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def generate_segment_prompt(conn, segment, api_key, all_characters):
    """为单个场景分段生成提示词"""
    segment_id, content = segment
    
    print(f"\n正在生成场景分段提示词: ID={segment_id}")
    print(f"内容: {content[:100]}...")
    
    # 提取文本中出现的人物
    characters_in_scene = extract_character_names(content, all_characters)
    
    if characters_in_scene:
        print(f"检测到人物: {', '.join([name for name, _ in characters_in_scene])}")
    else:
        print("未检测到已知人物")
    
    # 调用AI生成提示词
    prompt = generate_prompt_by_ai(api_key, content, characters_in_scene)
    if not prompt:
        print(f"生成提示词失败: ID={segment_id}")
        return False
    
    print(f"生成的提示词: {prompt[:100]}...")
    
    # 更新数据库
    if update_segment_prompt(conn, segment_id, prompt):
        print(f"场景分段提示词更新成功")
        return True
    else:
        print(f"场景分段提示词更新失败")
        return False

def main():
    """主函数"""
    print("开始生成场景分段提示词...")
    
    # 加载配置
    config = load_config()
    api_key = load_kimi_api_key(config)
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        print("\n" + "="*60)
        print("❌ 程序执行失败")
        print("未完成：数据库连接失败")
        print("="*60)
        return
    
    # 获取所有未生成提示词的场景分段
    segments = get_all_segments(conn)
    if not segments:
        print("没有找到未生成提示词的场景分段")
        conn.close()
        print("\n" + "="*60)
        print("⚠️  程序执行完成")
        print("已完成：连接数据库、检查场景分段")
        print("未完成：未找到未生成提示词的场景分段")
        print("="*60)
        return
    
    print(f"找到 {len(segments)} 个未生成提示词的场景分段")
    
    # 获取所有人物信息
    all_characters = get_all_characters(conn)
    print(f"找到 {len(all_characters)} 个人物信息")
    
    success_count = 0
    failed_count = 0
    
    # 串行生成提示词，避免API限流
    for segment in segments:
        if generate_segment_prompt(conn, segment, api_key, all_characters):
            success_count += 1
        else:
            failed_count += 1
        
        # 添加延迟，避免API速率限制
        time.sleep(1)
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ 程序执行完成")
    print(f"总计: {len(segments)} 个场景分段")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    
    if success_count == len(segments):
        print("\n已完成: 所有场景分段提示词生成")
    else:
        print("\n部分场景分段提示词生成失败")
    
    print("="*60)

if __name__ == "__main__":
    main()
