"""
程序名称：分析小说中出现三次以上的场景
功能描述：调用AI分析小说内容，统计并提取出现三次以上的重要场景，保存到数据库的scenes表中
作者：AI Assistant
日期：2026-03-30
"""
import os
import json
import pymysql
import requests

# 配置文件路径
CONFIG_FILE = 'db_config.json'
NOVEL_DIR = 'novel'
API_KEY_FILE = 'kimi api_key.txt'

def load_config():
    """加载数据库配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_api_key():
    """加载API密钥"""
    with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_novel_content(novel_title):
    """读取小说内容"""
    novel_path = os.path.join(NOVEL_DIR, novel_title)
    if not os.path.exists(novel_path):
        return None
    
    content = ""
    for filename in os.listdir(novel_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(novel_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content += f.read() + "\n\n"
            except Exception as e:
                print(f"读取文件 {filename} 失败: {e}")
    
    return content

def call_ai_api(api_key, content):
    """调用AI API分析小说中出现三次以上的场景"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 构建提示词
    prompt = f"""请详细分析以下小说内容，提取所有出现三次以上的重要场景。要求：

【场景提取要求】
1. 只提取小说中明确出现三次以上的重要场景（主要地点、环境、场所等）
2. 统计每个场景的出现次数
3. 每个场景的所有字段都必须提供具体、详细的描述，严禁使用"未提及"、"可推测"等模糊表述
4. 根据小说内容进行合理推断，但必须符合小说设定
5. 所有描述必须具体、生动、可用于漫画场景设计

【详细信息要求】
1. 基本信息：
   - 名称：场景名称，必须准确
   - 出现次数：准确统计在小说中出现的次数
   - 类型：场景类型（室内/室外/公共场所/私人场所/自然环境等）

2. 视觉细节描述（必须具体详细）：
   - 整体布局：场景的空间布局、结构特点
   - 建筑风格：建筑物的风格、年代、材质等
   - 环境元素：家具、装饰、植物、灯光等细节
   - 色彩氛围：主要色彩、光影效果、氛围营造

3. 时间与环境：
   - 时间段：早晨/中午/晚上/黄昏/深夜等
   - 天气情况：晴天/雨天/阴天/雪天等
   - 季节特征：春夏秋冬的特点

4. 氛围描述：
   - 整体氛围：温馨/紧张/神秘/压抑/热闹等
   - 音效环境：背景声音、环境音效等

5. 重要性评估：
   - 在故事中的重要程度（1-10，10为最重要）

【输出格式】
请用JSON数组格式返回，每个场景为一个对象，包含以下字段：
- name: 场景名称
- appearance_count: 出现次数（整数）
- description: 详细描述
- scene_type: 场景类型
- visual_details: 视觉细节描述
- atmosphere: 氛围描述
- time_period: 时间段
- weather: 天气情况
- importance: 重要性等级（1-10）

【示例格式】
[
    {{
        "name": "古玩店",
        "appearance_count": 8,
        "description": "一家位于老街上的古玩店，充满了古董和神秘气息",
        "scene_type": "室内",
        "visual_details": "店铺位于老旧街道的临街铺面，木质招牌上写着'古德斋'三个大字。店内光线昏暗，摆满了各种古董瓷器、字画、玉器等。货架上的瓷器泛着温润的光泽，墙上挂着几幅古画，空气中弥漫着淡淡的檀香和灰尘的味道。",
        "atmosphere": "神秘、古朴、充满历史感",
        "time_period": "白天",
        "weather": "晴天",
        "importance": 9
    }}
]

小说内容：
{content}"""  # 使用完整内容以确保统计准确
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "moonshot-v1-32k",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"API响应状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"API响应内容: {response.text}")
            return None
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"API调用失败: {e}")
        return None

def parse_ai_response(response_text):
    """解析AI响应"""
    try:
        # 尝试直接解析JSON数组
        return json.loads(response_text)
    except json.JSONDecodeError:
        # 尝试提取JSON部分
        start = response_text.find('[')
        end = response_text.rfind(']')
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            try:
                return json.loads(json_str)
            except:
                pass
        
        # 尝试提取单个JSON对象
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            try:
                return [json.loads(json_str)]
            except:
                pass
        return None

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

def save_scenes_to_db(conn, novel_id, scenes):
    """保存场景信息到数据库，避免重复插入类似场景"""
    if not conn or not scenes:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 获取已存在的场景名称列表
        cursor.execute("SELECT name FROM scenes WHERE novel_id = %s", (novel_id,))
        existing_scene_names = {row[0] for row in cursor.fetchall()}
        
        inserted_count = 0
        
        for scene in scenes:
            # 确保所有字段都是字符串或数字类型
            name = str(scene.get('name') or '')
            description = str(scene.get('description') or '')
            scene_type = str(scene.get('scene_type') or '')
            
            # 检查是否已存在类似场景
            if name in existing_scene_names:
                print(f"跳过已存在的场景: {name}")
                continue
            
            # 处理visual_details字段，如果是字典则转换为JSON字符串
            visual_details = scene.get('visual_details')
            if isinstance(visual_details, dict):
                visual_details = json.dumps(visual_details, ensure_ascii=False)
            else:
                visual_details = str(visual_details or '')
                
            atmosphere = str(scene.get('atmosphere') or '')
            time_period = str(scene.get('time_period') or '')
            weather = str(scene.get('weather') or '')
            
            # 处理数字字段，确保是整数
            appearance_count = scene.get('appearance_count')
            if appearance_count is not None:
                try:
                    appearance_count = int(appearance_count)
                except (ValueError, TypeError):
                    appearance_count = None
            
            importance = scene.get('importance')
            if importance is not None:
                try:
                    importance = int(importance)
                except (ValueError, TypeError):
                    importance = None
            
            cursor.execute("""
                INSERT INTO scenes (
                    novel_id, name, description, scene_type, appearance_count,
                    visual_details, atmosphere, time_period, weather, importance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novel_id,
                name,
                description,
                scene_type,
                appearance_count,
                visual_details,
                atmosphere,
                time_period,
                weather,
                importance
            ))
            
            inserted_count += 1
            existing_scene_names.add(name)
        
        conn.commit()
        print(f"成功插入 {inserted_count} 个新场景")
        return True
    except Exception as e:
        print(f"保存场景信息失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始分析小说中出现三次以上的场景...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 获取待分析的小说
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM novels WHERE analysis_status = 'analyzed'")
    novels = cursor.fetchall()
    cursor.close()
    
    if not novels:
        print("没有待分析场景的小说")
        conn.close()
        return
    
    print(f"找到 {len(novels)} 本待分析场景的小说")
    
    # 分析每本小说的场景
    for novel_id, novel_title in novels:
        print(f"\n正在分析小说场景: {novel_title}")
        
        # 读取小说内容
        content = get_novel_content(novel_title)
        if not content:
            print(f"无法读取小说内容: {novel_title}")
            continue
        
        # 调用AI API
        response = call_ai_api(api_key, content)
        if not response:
            print(f"AI分析失败: {novel_title}")
            continue
        
        # 解析结果
        scenes = parse_ai_response(response)
        if not scenes:
            print(f"解析AI响应失败: {novel_title}")
            continue
        
        print(f"找到 {len(scenes)} 个出现三次以上的场景")
        
        # 保存到数据库
        if save_scenes_to_db(conn, novel_id, scenes):
            print(f"成功保存场景信息: {novel_title}")
        else:
            print(f"保存场景信息失败: {novel_title}")
    
    conn.close()
    print("\n场景分析完成")

if __name__ == "__main__":
    main()