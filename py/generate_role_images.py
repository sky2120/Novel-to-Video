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
import time

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'
OUTPUT_DIR = 'images'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_api_key(config):
    """加载API密钥"""
    return config['api']['qwen_api_key']

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

def generate_prompt(character, angle_type):
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
    
    # 添加角度描述（保持角色特征一致）
    if angle_type == "front":
        prompt_parts.append("正面视角，面部特写，清晰的五官细节，保持角色特征一致性")
    elif angle_type == "side":
        prompt_parts.append("侧面视角，面部特写，侧脸轮廓清晰，保持角色特征一致性")
    elif angle_type == "half":
        prompt_parts.append("四分之三角度，面部特写，面部轮廓清晰，保持角色特征一致性")
    
    # 添加通用描述
    prompt_parts.append("漫画风格，国漫风格，线条清晰，色彩鲜明，角色立绘，高清细节，高质量渲染，纯白色背景，无文字，没有任何文字")
    
    return "，".join(prompt_parts)

def create_image_task(api_key, prompt):
    """创建异步图像生成任务"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-DashScope-Async": "enable"
    }
    
    data = {
        "model": "wanx2.0-t2i-turbo",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感，构图混乱，文字模糊，扭曲，乱码文字，无法辨认的文字，错误的文字，模糊的文字，文字扭曲，文字变形",
            "size": "1024*1024",  # 1:1比例
        },
        "stream": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"创建任务响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"创建任务响应内容: {response.text}")
            return None
        result = response.json()
        return result
    except Exception as e:
        print(f"创建任务失败: {e}")
        return None

def query_task_status(api_key, task_id):
    """查询任务状态"""
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"查询任务响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"查询任务响应内容: {response.text}")
            return None
        result = response.json()
        status = result.get("output", {}).get("task_status")
        print(f"任务状态: {status}")
        # 打印完整的输出信息
        if status == "FAILED":
            error_message = result.get("output", {}).get("message", "未知错误")
            print(f"任务失败原因: {error_message}")
        elif status == "SUCCEEDED":
            results = result.get("output", {}).get("results", [])
            print(f"任务成功，结果数量: {len(results)}")
        return result
    except Exception as e:
        print(f"查询任务失败: {e}")
        return None

def call_image_api(api_key, prompt):
    """调用文生图API生成角色图片（异步调用）"""
    import time
    
    # 创建任务
    task_result = create_image_task(api_key, prompt)
    if not task_result:
        return None
    
    task_id = task_result.get("output", {}).get("task_id")
    if not task_id:
        print("获取task_id失败")
        return None
    
    print(f"任务创建成功，task_id: {task_id}")
    
    # 轮询查询任务状态
    max_retries = 20
    retry_interval = 10
    
    for i in range(max_retries):
        print(f"第{i+1}次查询任务状态...")
        status_result = query_task_status(api_key, task_id)
        if not status_result:
            time.sleep(retry_interval)
            continue
        
        status = status_result.get("output", {}).get("task_status")
        if status == "SUCCEEDED":
            print("任务完成！")
            return status_result
        elif status == "FAILED":
            print(f"任务失败: {status_result.get('output', {}).get('message')}")
            return None
        
        time.sleep(retry_interval)
    
    print("任务超时")
    return None

def download_image(image_url, save_path):
    """下载并保存图片"""
    try:
        urllib.request.urlretrieve(image_url, save_path)
        return True
    except Exception as e:
        print(f"下载图片失败: {e}")
        return False

def update_character_image(conn, character_id, image_path, angle_type):
    """更新角色图片路径到数据库"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        # 根据角度类型更新对应的字段
        if angle_type == "标准脸1":
            field = "face_image_front"
        elif angle_type == "标准脸2":
            field = "face_image_side"
        elif angle_type == "标准脸3":
            field = "face_image_half"
        else:
            return False
        
        cursor.execute(f"""
            UPDATE characters 
            SET {field} = %s, is_generated = TRUE 
            WHERE id = %s
        """, (image_path, character_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新角色图片路径失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def generate_character_image(conn, character, novel_dir, api_key):
    """生成单个角色的图片"""
    character_id, name, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _ = character
    
    print(f"\n正在生成角色: {name}")
    
    # 为每个角色生成3张标准脸
    angle_types = [
        ("front", "标准脸1"),
        ("side", "标准脸2"),
        ("half", "标准脸3")
    ]
    
    # 生成3张不同角度的标准脸
    for angle_type, face_name in angle_types:
        print(f"\n生成{face_name} ({angle_type})...")
        
        # 生成提示词
        prompt = generate_prompt(character, angle_type)
        print(f"提示词: {prompt}")
        
        # 调用API生成图片
        result = call_image_api(api_key, prompt)
        if not result:
            print(f"生成图片失败: {name}_{face_name}")
            continue
        
        # 提取图片URL
        try:
            image_url = result['output']['results'][0]['url']
            print(f"图片URL: {image_url}")
            
            # 生成时间戳
            timestamp = str(int(time.time()))
            
            # 保存图片（使用时间戳命名，不包含中文）
            image_path = os.path.join(novel_dir, f"r_{timestamp}.png")
            if download_image(image_url, image_path):
                print(f"图片保存成功: {image_path}")
                
                # 更新数据库，存储本地图片路径
                if update_character_image(conn, character_id, image_path, face_name):
                    print(f"角色图片路径更新成功: {face_name}")
                else:
                    print(f"角色图片路径更新失败: {face_name}")
            else:
                print(f"图片保存失败: {face_name}")
                
            # 添加延迟，避免API速率限制
            time.sleep(2)
                
        except Exception as e:
            print(f"处理图片结果失败: {e}")
            print(f"结果结构: {result}")
    
    return character_id

def main():
    """主函数"""
    print("开始生成角色形象图片...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key(config)
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        print("\n" + "="*60)
        print("❌ 程序执行失败")
        print("未完成：数据库连接失败")
        print("="*60)
        return
    
    # 获取所有小说
    novels = get_all_novels(conn)
    if not novels:
        print("没有找到小说")
        conn.close()
        print("\n" + "="*60)
        print("⚠️  程序执行完成")
        print("已完成：连接数据库")
        print("未完成：未找到小说")
        print("="*60)
        return
    
    print(f"找到 {len(novels)} 本小说")
    
    total_characters = 0
    processed_characters = 0
    
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
        
        total_characters += len(characters)
        print(f"找到 {len(characters)} 个未生成的角色")
        
        # 串行生成图片，避免API限流
        for character in characters:
            character_id = generate_character_image(conn, character, novel_dir, api_key)
            processed_characters += 1
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ 程序执行完成")
    print(f"总计: {len(novels)} 本小说")
    print(f"角色总数: {total_characters} 个")
    print(f"已处理: {processed_characters} 个")
    
    if total_characters == processed_characters:
        print("\n已完成: 所有角色图片生成")
    else:
        print("\n部分角色图片生成可能失败")
    
    print("="*60)

if __name__ == "__main__":
    main()