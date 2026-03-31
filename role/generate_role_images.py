"""
程序名称：生成角色形象图片
功能描述：读取数据库中的角色信息，调用wanx2.0-t2i-turbo生成角色形象图片，保存到对应的小说文件夹中
作者：AI Assistant
日期：2026-03-31
"""
import os
import json
import pymysql
import requests
import urllib.request

# 配置文件路径
CONFIG_FILE = '../db_config.json'
API_KEY_FILE = '../qwen_apk_key.txt'
OUTPUT_DIR = '.'

def load_config():
    """加载数据库配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_api_key():
    """加载API密钥"""
    with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def connect_db(config):
    """连接数据库"""
    try:
        conn = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            charset=config['charset']
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def get_all_novels(conn):
    """获取所有小说信息"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title FROM novels")
        novels = cursor.fetchall()
        return novels
    except Exception as e:
        print(f"获取小说信息失败: {e}")
        return []
    finally:
        cursor.close()

def get_characters_by_novel(conn, novel_id):
    """获取指定小说的角色信息"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, age, gender, personality, identity, 
                   hairstyle, face_shape, eyes, eyebrows, nose_mouth, skin_color,
                   height_atmosphere, body_type, temperament, clothing_style,
                   color_scheme, signature_decoration, art_style
            FROM characters 
            WHERE novel_id = %s AND is_generated = FALSE
        """, (novel_id,))
        characters = cursor.fetchall()
        return characters
    except Exception as e:
        print(f"获取角色信息失败: {e}")
        return []
    finally:
        cursor.close()

def generate_prompt(character):
    """生成角色描述提示词"""
    (id, name, age, gender, personality, identity, hairstyle, face_shape, 
     eyes, eyebrows, nose_mouth, skin_color, height_atmosphere, body_type, 
     temperament, clothing_style, color_scheme, signature_decoration, art_style) = character
    
    # 构建详细的角色描述
    prompt_parts = []
    
    # 基础信息
    if name:
        prompt_parts.append(f"角色名称：{name}")
    if age:
        prompt_parts.append(f"年龄：{age}岁")
    if gender:
        prompt_parts.append(f"性别：{gender}")
    if personality:
        prompt_parts.append(f"性格：{personality}")
    if identity:
        prompt_parts.append(f"身份：{identity}")
    
    # 外貌特征
    appearance_parts = []
    if hairstyle:
        appearance_parts.append(f"发型：{hairstyle}")
    if face_shape:
        appearance_parts.append(f"脸型：{face_shape}")
    if eyes:
        appearance_parts.append(f"眼睛：{eyes}")
    if eyebrows:
        appearance_parts.append(f"眉毛：{eyebrows}")
    if nose_mouth:
        appearance_parts.append(f"鼻子和嘴巴：{nose_mouth}")
    if skin_color:
        appearance_parts.append(f"肤色：{skin_color}")
    
    if appearance_parts:
        prompt_parts.append("外貌特征：" + "，".join(appearance_parts))
    
    # 体型与气质
    if height_atmosphere:
        prompt_parts.append(f"身高：{height_atmosphere}")
    if body_type:
        prompt_parts.append(f"体型：{body_type}")
    if temperament:
        prompt_parts.append(f"气质：{temperament}")
    
    # 服装信息
    clothing_parts = []
    if clothing_style:
        clothing_parts.append(f"服装风格：{clothing_style}")
    if color_scheme:
        clothing_parts.append(f"配色：{color_scheme}")
    if signature_decoration:
        clothing_parts.append(f"标志性装饰：{signature_decoration}")
    
    if clothing_parts:
        prompt_parts.append("服装信息：" + "，".join(clothing_parts))
    
    # 漫画风格
    if art_style:
        prompt_parts.append(f"漫画风格：{art_style}")
    
    # 添加通用描述
    prompt_parts.append("高清细节，高质量渲染，3D渲染，动漫风格，角色立绘")
    
    return "，".join(prompt_parts)

def call_image_api(api_key, prompt):
    """调用文生图API生成角色图片"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "wanx2.0-t2i-turbo",
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        },
        "parameters": {
            "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感，构图混乱，文字模糊，扭曲",
            "prompt_extend": True,
            "watermark": False,
            "size": "2688*1536"  # 16:9比例
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"API响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"API响应内容: {response.text}")
            return None
        result = response.json()
        return result
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

def download_image(image_url, save_path):
    """下载并保存图片"""
    try:
        urllib.request.urlretrieve(image_url, save_path)
        return True
    except Exception as e:
        print(f"下载图片失败: {e}")
        return False

def update_character_status(conn, character_id):
    """更新角色生成状态"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE characters 
            SET is_generated = TRUE 
            WHERE id = %s
        """, (character_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"更新角色状态失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始生成角色形象图片...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 获取所有小说
    novels = get_all_novels(conn)
    if not novels:
        print("没有找到小说")
        conn.close()
        return
    
    print(f"找到 {len(novels)} 本小说")
    
    # 处理每本小说
    for novel_id, novel_title in novels:
        print(f"\n正在处理小说: {novel_title}")
        
        # 创建小说文件夹
        novel_dir = os.path.join(OUTPUT_DIR, novel_title)
        os.makedirs(novel_dir, exist_ok=True)
        
        # 获取角色信息
        characters = get_characters_by_novel(conn, novel_id)
        if not characters:
            print(f"没有找到未生成的角色")
            continue
        
        print(f"找到 {len(characters)} 个未生成的角色")
        
        # 为每个角色生成图片
        for character in characters:
            character_id, name, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = character
            
            print(f"\n正在生成角色: {name}")
            
            # 生成提示词
            prompt = generate_prompt(character)
            print(f"提示词: {prompt}")
            
            # 调用API生成图片
            result = call_image_api(api_key, prompt)
            if not result:
                print(f"生成图片失败: {name}")
                continue
            
            # 提取图片URL
            try:
                image_url = result['output']['choices'][0]['message']['content'][0]['image']
                print(f"图片URL: {image_url}")
                
                # 保存图片
                image_path = os.path.join(novel_dir, f"{name}.png")
                if download_image(image_url, image_path):
                    print(f"图片保存成功: {image_path}")
                    
                    # 更新角色状态
                    if update_character_status(conn, character_id):
                        print(f"角色状态更新成功")
                    else:
                        print(f"角色状态更新失败")
                else:
                    print(f"图片保存失败: {name}")
                    
            except Exception as e:
                print(f"处理图片结果失败: {e}")
    
    conn.close()
    print("\n角色图片生成完成")

if __name__ == "__main__":
    main()