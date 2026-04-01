"""
程序名称：生成场景分段图片
功能描述：读取数据库中的scene_segments表内容，调用wanx2.0-t2i-turbo生成场景图片，保存到指定目录并更新数据库
作者：AI Assistant
日期：2026-04-01
"""
import os
import json
import pymysql
import requests
import urllib.request
import time

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'
OUTPUT_DIR = 'images/逆天改命法宝'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_api_key(config):
    """加载API密钥"""
    return config['api']['qwen_api_key']

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
    """获取所有未生成图片的场景分段"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, content, image_prompt FROM scene_segments 
            WHERE image_url IS NULL OR image_url = ''
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

def generate_prompt(image_prompt):
    """使用数据库中存储的提示词生成图片"""
    prompt_parts = []
    
    # 使用数据库中存储的提示词
    prompt_parts.append(image_prompt)
    
    # 添加通用描述
    prompt_parts.append("场景插画，漫画风格，国漫风格，线条清晰，色彩鲜明，高清细节，高质量渲染，用装饰图案代替文字，招牌用装饰图案，菜单用装饰图案，无真实文字，包含人物，固定场景")
    
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
            "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感，构图混乱，真实文字，文字内容，文字符号，文字字母，文字数字，乱码文字，无法辨认的文字，错误的文字，模糊的文字，文字扭曲，文字变形",
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
    """调用文生图API生成场景图片（异步调用）"""
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

def update_segment_image(conn, segment_id, image_path):
    """更新场景分段图片路径到数据库"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scene_segments 
            SET image_url = %s 
            WHERE id = %s
        """, (image_path, segment_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新场景分段图片路径失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def generate_segment_image(conn, segment, output_dir, api_key):
    """生成单个场景分段的图片"""
    segment_id, content, image_prompt = segment
    
    print(f"\n正在生成场景分段: ID={segment_id}")
    print(f"内容: {content[:100]}...")
    
    if not image_prompt:
        print(f"错误: 场景分段 {segment_id} 没有提示词")
        return False
    
    print(f"使用数据库中的提示词: {image_prompt[:100]}...")
    
    # 生成提示词
    prompt = generate_prompt(image_prompt)
    print(f"最终提示词: {prompt}")
    
    # 调用API生成图片
    result = call_image_api(api_key, prompt)
    if not result:
        print(f"生成图片失败: ID={segment_id}")
        return False
    
    # 提取图片URL
    try:
        image_url = result['output']['results'][0]['url']
        print(f"图片URL: {image_url}")
        
        # 生成时间戳
        timestamp = str(int(time.time()))
        
        # 保存图片（使用时间戳命名，不包含中文）
        image_path = os.path.join(output_dir, f"seg_{timestamp}.png")
        if download_image(image_url, image_path):
            print(f"图片保存成功: {image_path}")
            
            # 更新数据库，存储本地图片路径
            if update_segment_image(conn, segment_id, image_path):
                print(f"场景分段图片路径更新成功")
                return True
            else:
                print(f"场景分段图片路径更新失败")
        else:
            print(f"图片保存失败")
            
        # 添加延迟，避免API速率限制
        time.sleep(2)
            
    except Exception as e:
        print(f"处理图片结果失败: {e}")
        print(f"结果结构: {result}")
    
    return False

def main():
    """主函数"""
    print("开始生成场景分段图片...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key(config)
    
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        print("\n" + "="*60)
        print("❌ 程序执行失败")
        print("未完成：数据库连接失败")
        print("="*60)
        return
    
    # 获取所有未生成图片的场景分段
    segments = get_all_segments(conn)
    if not segments:
        print("没有找到未生成图片的场景分段")
        conn.close()
        print("\n" + "="*60)
        print("⚠️  程序执行完成")
        print("已完成：连接数据库、检查场景分段")
        print("未完成：未找到未生成图片的场景分段")
        print("="*60)
        return
    
    print(f"找到 {len(segments)} 个未生成图片的场景分段")
    
    success_count = 0
    failed_count = 0
    
    # 串行生成图片，避免API限流
    for segment in segments:
        if generate_segment_image(conn, segment, OUTPUT_DIR, api_key):
            success_count += 1
        else:
            failed_count += 1
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ 程序执行完成")
    print(f"总计: {len(segments)} 个场景分段")
    print(f"成功: {success_count} 个")
    print(f"失败: {failed_count} 个")
    
    if success_count == len(segments):
        print("\n已完成: 所有场景分段图片生成")
    else:
        print("\n部分场景分段图片生成失败")
    
    print("="*60)

if __name__ == "__main__":
    main()
