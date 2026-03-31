"""
程序名称：生成场景形象图片
功能描述：读取数据库中的场景信息，调用wanx2.0-t2i-turbo生成场景形象图片，保存到对应的小说文件夹中
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
CONFIG_FILE = 'db_config.json'
API_KEY_FILE = 'qwen_apk_key.txt'
OUTPUT_DIR = 'images'

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

def get_scenes_by_novel(conn, novel_id):
    """获取指定小说的场景信息"""
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, name, description, scene_type, appearance_count, 
                   visual_details, atmosphere, time_period, weather, importance
            FROM scenes 
            WHERE novel_id = %s AND is_generated = FALSE
        """, (novel_id,))
        scenes = cursor.fetchall()
        return scenes
    except Exception as e:
        print(f"获取场景信息失败: {e}")
        return []
    finally:
        cursor.close()

def generate_prompt(scene):
    """生成场景描述提示词"""
    (id, name, description, scene_type, appearance_count, 
     visual_details, atmosphere, time_period, weather, importance) = scene
    
    # 构建详细的场景描述
    prompt_parts = []
    
    # 基础信息
    if name:
        prompt_parts.append(f"场景名称：{name}")
    if scene_type:
        prompt_parts.append(f"场景类型：{scene_type}")
    
    # 视觉细节
    if visual_details:
        prompt_parts.append(f"视觉细节：{visual_details}")
    
    # 氛围描述
    if atmosphere:
        prompt_parts.append(f"氛围描述：{atmosphere}")
    
    # 时间和天气
    if time_period:
        prompt_parts.append(f"时间段：{time_period}")
    if weather:
        prompt_parts.append(f"天气情况：{weather}")
    
    # 其他描述
    if description:
        prompt_parts.append(f"详细描述：{description}")
    
    # 添加通用描述
    prompt_parts.append("场景插画，漫画风格，国漫风格，线条清晰，色彩鲜明，高清细节，高质量渲染，用装饰图案代替文字，招牌用装饰图案，菜单用装饰图案，无真实文字，无人，没有人物，固定场景")
    
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
            "negative_prompt": "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感，构图混乱，真实文字，文字内容，文字符号，文字字母，文字数字，乱码文字，无法辨认的文字，错误的文字，模糊的文字，文字扭曲，文字变形，人物，人像，人脸，人影，人体，人物轮廓，人物形象",
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

def update_scene_status(conn, scene_id):
    """更新场景生成状态"""
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scenes 
            SET is_generated = TRUE 
            WHERE id = %s
        """, (scene_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"更新场景状态失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def generate_scene_image(scene, novel_dir, api_key):
    """生成单个场景的图片"""
    scene_id, name, _, _, _, _, _, _, _, _ = scene
    
    print(f"\n正在生成场景: {name}")
    
    # 生成提示词
    prompt = generate_prompt(scene)
    print(f"提示词: {prompt}")
    
    # 调用API生成图片
    result = call_image_api(api_key, prompt)
    if not result:
        print(f"生成图片失败: {name}")
        return scene_id
    
    # 提取图片URL
    try:
        image_url = result['output']['results'][0]['url']
        print(f"图片URL: {image_url}")
        
        # 生成时间戳
        timestamp = str(int(time.time()))
        
        # 保存图片（按照命名规范）
        image_path = os.path.join(novel_dir, f"{name}_场景_{timestamp}.png")
        if download_image(image_url, image_path):
            print(f"图片保存成功: {image_path}")
        else:
            print(f"图片保存失败: {name}")
            
        # 添加延迟，避免API速率限制
        time.sleep(2)
            
    except Exception as e:
        print(f"处理图片结果失败: {e}")
        print(f"结果结构: {result}")
    
    return scene_id

def main():
    """主函数"""
    print("开始生成场景形象图片...")
    
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
        
        # 获取场景信息
        scenes = get_scenes_by_novel(conn, novel_id)
        if not scenes:
            print(f"没有找到未生成的场景")
            continue
        
        print(f"找到 {len(scenes)} 个未生成的场景")
        
        # 串行生成图片，避免API限流
        for scene in scenes:
            scene_id = generate_scene_image(scene, novel_dir, api_key)
            if update_scene_status(conn, scene_id):
                print(f"场景状态更新成功: ID={scene_id}")
            else:
                print(f"场景状态更新失败: ID={scene_id}")
    
    conn.close()
    print("\n场景图片生成完成")

if __name__ == "__main__":
    main()
