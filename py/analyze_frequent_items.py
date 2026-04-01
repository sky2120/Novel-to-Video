"""
程序名称：分析小说中出现三次以上的物品
功能描述：调用AI分析小说内容，统计并提取出现三次以上的重要物品，保存到数据库的items表中
作者：AI Assistant
日期：2026-03-30
"""
import os
import json
import pymysql
import requests

# 配置文件路径
CONFIG_FILE = 'config.json'
NOVEL_DIR = 'novel'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_api_key(config):
    """加载API密钥"""
    return config['api']['kimi_api_key']

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
    """调用AI API分析小说中出现三次以上的物品"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 构建提示词
    prompt = f"""请详细分析以下小说内容，提取所有出现三次以上的重要物品。要求：

【物品提取要求】
1. 只提取小说中明确出现三次以上的物品（关键道具、武器、法器、特殊物品等）
2. 统计每个物品的出现次数
3. 每个物品的所有字段都必须提供具体、详细的描述，严禁使用"未提及"、"可推测"等模糊表述
4. 根据小说内容进行合理推断，但必须符合小说设定
5. 所有描述必须具体、生动、可用于漫画道具设计

【详细信息要求】
1. 基本信息：
   - 名称：必须准确
   - 出现次数：准确统计在小说中出现的次数
   - 类型：具体分类（武器/道具/法器/药品/食物/交通工具/法宝等）
   - 稀有度：普通/稀有/史诗/传说/神器等

2. 外观描述（必须具体详细）：
   - 外观：详细描述物品的形状、颜色、材质、大小等特征
   - 细节：特殊标记、纹路、光泽等细节描述

3. 功能作用：
   - 功能：详细描述物品的主要功能和作用
   - 效果：使用效果、能力范围、限制条件等

4. 背景信息：
   - 来源：物品的起源、出处、历史背景
   - 持有者：当前持有者或历史持有者
   - 重要性：在故事中的重要程度（1-10，10为最重要）

【输出格式】
请用JSON数组格式返回，每个物品为一个对象，包含以下字段：
- name: 物品名称
- appearance_count: 出现次数（整数）
- description: 详细描述
- item_type: 物品类型
- item_function: 功能和作用
- rarity: 稀有度
- appearance: 外观描述
- origin: 物品来源
- owner: 物品持有者
- importance: 重要性等级（1-10）

【示例格式】
[
    {{
        "name": "琉璃珠",
        "appearance_count": 15,
        "description": "一个神秘的绿色琉璃珠子，具有神奇的透视能力",
        "item_type": "法宝",
        "item_function": "可以看穿物体内部，鉴定古玩真伪，寻找宝藏",
        "rarity": "传说",
        "appearance": "绿色琉璃材质，圆形，直径约2厘米，表面有神秘纹路，在阳光下会发出奇异光芒",
        "origin": "神秘老乞丐赠送",
        "owner": "杨波",
        "importance": 10
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

def save_items_to_db(conn, novel_id, items):
    """保存物品信息到数据库，避免重复插入类似物品"""
    if not conn or not items:
        return False
    
    cursor = conn.cursor()
    
    try:
        # 获取已存在的物品名称列表
        cursor.execute("SELECT name FROM items WHERE novel_id = %s", (novel_id,))
        existing_item_names = {row[0] for row in cursor.fetchall()}
        
        inserted_count = 0
        
        for item in items:
            name = item.get('name')
            
            # 检查是否已存在类似物品
            if name in existing_item_names:
                print(f"跳过已存在的物品: {name}")
                continue
            
            # 处理数字字段，确保是整数
            appearance_count = item.get('appearance_count')
            if appearance_count is not None:
                try:
                    appearance_count = int(appearance_count)
                except (ValueError, TypeError):
                    appearance_count = None
            
            importance = item.get('importance')
            if importance is not None:
                try:
                    importance = int(importance)
                except (ValueError, TypeError):
                    importance = None
            
            cursor.execute("""
                INSERT INTO items (
                    novel_id, name, description, item_type, item_function,
                    rarity, appearance, origin, owner, importance
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                novel_id,
                name,
                str(item.get('description') or ''),
                str(item.get('item_type') or ''),
                str(item.get('item_function') or ''),
                str(item.get('rarity') or ''),
                str(item.get('appearance') or ''),
                str(item.get('origin') or ''),
                str(item.get('owner') or ''),
                importance
            ))
            
            inserted_count += 1
            existing_item_names.add(name)
        
        conn.commit()
        print(f"成功插入 {inserted_count} 个新物品")
        return True
    except Exception as e:
        print(f"保存物品信息失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始分析小说中出现三次以上的物品...")
    
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
    
    # 获取待分析的小说
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM novels WHERE analysis_status = 'analyzed'")
    novels = cursor.fetchall()
    cursor.close()
    
    if not novels:
        print("没有待分析物品的小说")
        conn.close()
        print("\n" + "="*60)
        print("⚠️  程序执行完成")
        print("已完成：连接数据库、检查待分析小说")
        print("未完成：未找到待分析物品的小说")
        print("="*60)
        return
    
    print(f"找到 {len(novels)} 本待分析物品的小说")
    
    success_count = 0
    failed_count = 0
    success_novels = []
    failed_novels = []
    
    # 分析每本小说的物品
    for novel_id, novel_title in novels:
        print(f"\n正在分析小说物品: {novel_title}")
        
        # 读取小说内容
        content = get_novel_content(novel_title)
        if not content:
            print(f"无法读取小说内容: {novel_title}")
            failed_count += 1
            failed_novels.append(novel_title)
            continue
        
        # 调用AI API
        response = call_ai_api(api_key, content)
        if not response:
            print(f"AI分析失败: {novel_title}")
            failed_count += 1
            failed_novels.append(novel_title)
            continue
        
        # 解析结果
        items = parse_ai_response(response)
        if not items:
            print(f"解析AI响应失败: {novel_title}")
            failed_count += 1
            failed_novels.append(novel_title)
            continue
        
        print(f"找到 {len(items)} 个出现三次以上的物品")
        
        # 保存到数据库
        if save_items_to_db(conn, novel_id, items):
            print(f"成功保存物品信息: {novel_title}")
            success_count += 1
            success_novels.append(novel_title)
        else:
            print(f"保存物品信息失败: {novel_title}")
            failed_count += 1
            failed_novels.append(novel_title)
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ 程序执行完成")
    print(f"总计: {len(novels)} 本小说")
    print(f"成功: {success_count} 本")
    print(f"失败: {failed_count} 本")
    
    if success_novels:
        print("\n已完成:")
        for novel in success_novels:
            print(f"  - {novel}")
    
    if failed_novels:
        print("\n未完成:")
        for novel in failed_novels:
            print(f"  - {novel}")
    
    print("="*60)

if __name__ == "__main__":
    main()