"""
程序名称：分析小说角色信息
功能描述：调用AI分析小说内容，提取所有主要角色的详细信息（包括身份、外貌、体型、气质、服装等），保存到数据库的characters表中
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
    """调用AI API分析小说角色"""
    url = "https://api.moonshot.cn/v1/chat/completions"
    
    # 构建提示词
    prompt = f"""请详细分析以下小说内容，提取所有主要角色的精确信息。要求：

【角色提取要求】
1. 只提取小说中明确出现的主要角色（主角、重要配角、反派）
2. 每个角色的所有字段都必须提供具体、详细的描述，严禁使用"未提及"、"可推测"等模糊表述
3. 根据小说内容进行合理推断，但必须符合小说设定
4. 所有描述必须具体、生动、可用于漫画角色设计

【详细信息要求】
1. 基础身份：
   - 姓名：必须准确
   - 年龄：根据小说描述推断具体年龄（如20岁、35岁等）
   - 性别：男/女/中性
   - 性格：选择最符合的2-3个性格标签（高冷/温柔/腹黑/阳光/病娇/奸诈/精明/坚韧等）
   - 身份：具体职业或身份（古玩店学徒/古玩店老板/学生/总裁等）

2. 外貌核心（必须具体详细）：
   - 发型：具体描述长度（短发/中长发/长发）、颜色（黑色/棕色/金色等）、样式（直发/卷发/高马尾/齐刘海/板寸等）
   - 脸型：具体脸型（瓜子脸/圆脸/方脸/鹅蛋脸/菱形脸/少年感窄脸等）
   - 眼睛：具体颜色（黑色/棕色/蓝色等）、形状（杏眼/桃花眼/丹凤眼/圆眼/细长眼等）
   - 眉毛：具体样式（平眉/剑眉/细眉/浓眉/弯眉等）
   - 鼻子/嘴巴：具体描述（高鼻梁/塌鼻梁/薄唇/厚唇/樱桃小嘴等）
   - 肤色：具体描述（冷白皮/暖白皮/健康小麦色/古铜色等）

3. 体型与气质：
   - 身高氛围：具体描述（高挑/中等/娇小/魁梧/少年感等）
   - 体型：具体描述（纤细/匀称/肌肉/偏胖/瘦弱等）
   - 气质：具体描述（清冷/魅惑/阳光/阴郁/霸气/精明/憨厚等）

4. 服装（必须具体）：
   - 主服装风格：现代休闲/商务正装/古风汉服/校服/运动装等
   - 固定配色：具体颜色组合（黑色+白色/深蓝色+灰色/红色+黑色等）
   - 标志性装饰：具体配饰（黑框眼镜/银色项链/红色发带/机械义眼/风衣等）

5. 漫画风格：国漫风

【输出格式】
请用JSON数组格式返回，每个角色为一个对象，包含以下字段：
- name: 姓名
- age: 年龄（整数）
- gender: 性别
- personality: 性格
- identity: 身份
- hairstyle: 发型（详细描述）
- face_shape: 脸型
- eyes: 眼睛（详细描述）
- eyebrows: 眉毛
- nose_mouth: 鼻子/嘴巴（详细描述）
- skin_color: 肤色
- height_atmosphere: 身高氛围
- body_type: 体型
- temperament: 气质
- clothing_style: 主服装风格
- color_scheme: 固定配色
- signature_decoration: 标志性装饰
- art_style: 漫画风格

【示例格式】
[
    {{
        "name": "杨波",
        "age": 20,
        "gender": "男",
        "personality": "阳光、坚韧、善良",
        "identity": "古玩店学徒",
        "hairstyle": "黑色短发，干净利落",
        "face_shape": "少年感窄脸",
        "eyes": "黑色杏眼，眼神清澈",
        "eyebrows": "剑眉",
        "nose_mouth": "高鼻梁，薄唇",
        "skin_color": "健康小麦色",
        "height_atmosphere": "中等身高",
        "body_type": "匀称",
        "temperament": "阳光开朗",
        "clothing_style": "现代休闲",
        "color_scheme": "蓝色+白色",
        "signature_decoration": "无",
        "art_style": "国漫风"
    }}
]

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

def save_characters_to_db(conn, novel_id, characters):
    """保存角色信息到数据库"""
    if not conn or not characters:
        return False
    
    cursor = conn.cursor()
    
    try:
        for character in characters:
            # 处理年龄字段，确保是整数
            age = character.get('age')
            if age is not None:
                try:
                    age = int(age)
                except (ValueError, TypeError):
                    age = None
            
            cursor.execute("""
                INSERT INTO characters (
                    novel_id, name, age, gender, personality, identity,
                    hairstyle, face_shape, eyes, eyebrows, nose_mouth,
                    skin_color, height_atmosphere, body_type, temperament,
                    clothing_style, color_scheme, signature_decoration, art_style
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    age = VALUES(age),
                    gender = VALUES(gender),
                    personality = VALUES(personality),
                    identity = VALUES(identity),
                    hairstyle = VALUES(hairstyle),
                    face_shape = VALUES(face_shape),
                    eyes = VALUES(eyes),
                    eyebrows = VALUES(eyebrows),
                    nose_mouth = VALUES(nose_mouth),
                    skin_color = VALUES(skin_color),
                    height_atmosphere = VALUES(height_atmosphere),
                    body_type = VALUES(body_type),
                    temperament = VALUES(temperament),
                    clothing_style = VALUES(clothing_style),
                    color_scheme = VALUES(color_scheme),
                    signature_decoration = VALUES(signature_decoration),
                    art_style = VALUES(art_style),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                novel_id,
                character.get('name'),
                age,
                character.get('gender'),
                character.get('personality'),
                character.get('identity'),
                character.get('hairstyle'),
                character.get('face_shape'),
                character.get('eyes'),
                character.get('eyebrows'),
                character.get('nose_mouth'),
                character.get('skin_color'),
                character.get('height_atmosphere'),
                character.get('body_type'),
                character.get('temperament'),
                character.get('clothing_style'),
                character.get('color_scheme'),
                character.get('signature_decoration'),
                character.get('art_style')
            ))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存角色信息失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始分析小说角色信息...")
    
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
        print("没有待分析角色的小说")
        conn.close()
        return
    
    print(f"找到 {len(novels)} 本待分析角色的小说")
    
    # 分析每本小说的角色
    for novel_id, novel_title in novels:
        print(f"\n正在分析小说角色: {novel_title}")
        
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
        characters = parse_ai_response(response)
        if not characters:
            print(f"解析AI响应失败: {novel_title}")
            continue
        
        print(f"找到 {len(characters)} 个角色")
        
        # 保存到数据库
        if save_characters_to_db(conn, novel_id, characters):
            print(f"成功保存角色信息: {novel_title}")
        else:
            print(f"保存角色信息失败: {novel_title}")
    
    conn.close()
    print("\n角色分析完成")

if __name__ == "__main__":
    main()