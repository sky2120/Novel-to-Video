"""
程序名称：分析小说风格和主角信息
功能描述：调用AI分析小说内容，提取小说类型、视觉风格、艺术风格、背景设置、主角信息和风格提示词，更新到数据库
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
API_KEY_FILE = 'qwen_apk_key.txt'

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
    """调用AI API分析小说"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 构建提示词
    prompt = f"""请分析以下小说内容，提取以下信息：
1. 小说类型（如玄幻、仙侠、都市、科幻等）
2. 视觉风格（如漫画风、写实风、水彩风等）
3. 艺术风格（如日式、美式、中式等）
4. 背景设置（如现代都市、古代仙侠、未来科幻等）
5. 主角名称和特征描述
6. 主要风格提示词（用于AI图像生成）

请用JSON格式返回结果，包含以下字段：
- genre: 小说类型
- visual_style: 视觉风格
- art_style: 艺术风格
- background_setting: 背景设置
- protagonist: 主角名称
- protagonist_description: 主角特征描述
- style_prompt: 风格提示词

小说内容：
{content[:2000]}"""  # 限制内容长度，避免超出API限制
    
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
        # 尝试直接解析JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # 尝试提取JSON部分
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            try:
                return json.loads(json_str)
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

def update_novel_info(conn, novel_id, analysis_result):
    """更新小说信息到数据库"""
    if not conn or not analysis_result:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE novels 
            SET genre = %s, 
                visual_style = %s, 
                art_style = %s, 
                background_setting = %s, 
                protagonist = %s,
                style_prompt = %s,
                analysis_status = 'analyzed',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            analysis_result.get('genre'),
            analysis_result.get('visual_style'),
            analysis_result.get('art_style'),
            analysis_result.get('background_setting'),
            analysis_result.get('protagonist'),
            analysis_result.get('style_prompt'),
            novel_id
        ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新数据库失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始分析小说风格和角色...")
    
    # 加载配置
    config = load_config()
    api_key = load_api_key()
    
    # 连接数据库
    conn = connect_db(config)
    if not conn:
        return
    
    # 获取待分析的小说
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM novels WHERE analysis_status = 'pending'")
    novels = cursor.fetchall()
    cursor.close()
    
    if not novels:
        print("没有待分析的小说")
        conn.close()
        return
    
    print(f"找到 {len(novels)} 本待分析的小说")
    
    # 分析每本小说
    for novel_id, novel_title in novels:
        print(f"\n正在分析小说: {novel_title}")
        
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
        analysis_result = parse_ai_response(response)
        if not analysis_result:
            print(f"解析AI响应失败: {novel_title}")
            continue
        
        print(f"分析结果: {analysis_result}")
        
        # 更新数据库
        if update_novel_info(conn, novel_id, analysis_result):
            print(f"成功更新小说信息: {novel_title}")
        else:
            print(f"更新小说信息失败: {novel_title}")
    
    conn.close()
    print("\n分析完成")

if __name__ == "__main__":
    main()