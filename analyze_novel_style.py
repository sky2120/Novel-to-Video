import os
import json
import re
import pymysql
from pathlib import Path

class NovelStyleAnalyzer:
    def __init__(self):
        self.db_config = self._load_db_config()
        self.novel_base_path = r'd:\桌面\临时文件\A自动生成类型文件\AI漫剧\novel'
        self.api_key_file = r'd:\桌面\临时文件\A自动生成类型文件\AI漫剧\kimi api_key.txt'
    
    def _load_db_config(self):
        """从配置文件加载数据库连接信息"""
        config_file = 'db_config.json'
        default_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'username',
            'password': 'password',
            'database': 'database',
            'charset': 'utf8mb4'
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"已从 {config_file} 加载数据库配置")
            return config
        except FileNotFoundError:
            print(f"警告：未找到 {config_file} 文件，使用默认配置")
            return default_config
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return default_config
    
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = pymysql.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return None
    
    def get_api_key(self):
        """获取API密钥"""
        try:
            with open(self.api_key_file, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
            return api_key
        except Exception as e:
            print(f"读取API密钥失败: {e}")
            return None
    
    def read_novel_content(self, novel_folder):
        """读取小说所有章节内容"""
        chapters = []
        novel_path = Path(self.novel_base_path) / novel_folder
        
        for chapter_file in sorted(novel_path.iterdir()):
            if chapter_file.is_file() and chapter_file.suffix == '.txt':
                try:
                    with open(chapter_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    chapters.append({
                        'title': chapter_file.stem,
                        'content': content
                    })
                    print(f"读取章节: {chapter_file.stem}")
                except Exception as e:
                    print(f"读取文件失败: {chapter_file.name}, 错误: {e}")
        
        return chapters
    
    def call_ai_analysis(self, novel_title, chapters):
        """调用AI分析小说风格和背景"""
        import requests
        
        api_key = self.get_api_key()
        if not api_key:
            return None
        
        endpoint = "https://api.moonshot.cn/v1/chat/completions"
        
        # 构建系统提示词
        system_prompt = """你是一个专业的文学分析专家，擅长分析小说的风格、背景、角色等元素。请根据提供的小说内容，分析并输出以下信息：
        
1. 风格分析：小说的整体风格（如：古风、现代、科幻、奇幻、悬疑、言情等）
2. 背景设定：故事发生的时代背景、地点环境等
3. 主角分析：主要角色的外貌特征、性格特点、服装风格等
4. 画面风格：适合的画面风格描述（用于AI图像生成）
5. 色彩基调：整体的色彩风格和配色方案

请以JSON格式输出，不要包含任何额外的解释性文字。JSON格式如下：
{
    "style": {
        "genre": "风格类型",
        "description": "详细风格描述"
    },
    "background": {
        "era": "时代背景",
        "setting": "地点环境",
        "atmosphere": "整体氛围"
    },
    "protagonist": {
        "name": "主角名称",
        "appearance": "外貌特征",
        "personality": "性格特点",
        "clothing": "服装风格"
    },
    "visual_style": {
        "art_style": "画面风格",
        "color_palette": "色彩基调",
        "lighting": "光影风格"
    }
}"""
        
        # 构建用户提示词
        chapters_text = ""
        for chapter in chapters[:3]:  # 只使用前3章进行分析，避免token过多
            chapters_text += f"【{chapter['title']}】\n{chapter['content'][:1000]}\n\n"  # 每章取前1000字
        
        user_prompt = f"""请分析以下小说《{novel_title}》的内容，提取风格、背景、主角和视觉风格信息：

{chapters_text}"""
        
        # 构建请求体
        payload = {
            "model": "kimi-k2.5",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "max_tokens": 2000
        }
        
        # 发送请求
        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps(payload)
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and result["choices"]:
                ai_response = result["choices"][0]["message"]["content"]
                print("AI原始回复:")
                print(ai_response)
                print("-" * 50)
                
                try:
                    # 尝试解析JSON
                    parsed_result = json.loads(ai_response)
                    return parsed_result
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
                    # 尝试提取JSON部分
                    try:
                        # 查找JSON开始和结束位置
                        start_idx = ai_response.find('{')
                        end_idx = ai_response.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            json_str = ai_response[start_idx:end_idx+1]
                            parsed_result = json.loads(json_str)
                            print("成功提取并解析JSON部分")
                            return parsed_result
                    except Exception as e2:
                        print(f"提取JSON部分失败: {e2}")
                    return None
            else:
                print("API返回格式异常")
                print(f"API返回: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
    
    def save_to_database(self, novel_title, analysis_result):
        """将分析结果保存到数据库"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 更新小说表
            update_sql = """
            UPDATE novels 
            SET description = %s, 
                cover_url = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE title = %s
            """
            
            # 构建描述信息
            style_desc = analysis_result.get('style', {}).get('description', '')
            background_desc = analysis_result.get('background', {}).get('setting', '')
            protagonist_desc = analysis_result.get('protagonist', {}).get('appearance', '')
            
            description = f"风格：{style_desc}\n背景：{background_desc}\n主角：{protagonist_desc}"
            
            # 保存视觉风格信息到metadata字段（如果有）
            metadata = {
                'visual_style': analysis_result.get('visual_style', {}),
                'style_analysis': analysis_result.get('style', {}),
                'background_setting': analysis_result.get('background', {})
            }
            
            cursor.execute(update_sql, (description, None, novel_title))
            
            if cursor.rowcount > 0:
                print(f"成功更新小说《{novel_title}》的风格信息")
                conn.commit()
                return True
            else:
                print(f"未找到小说《{novel_title}》")
                return False
                
        except Exception as e:
            print(f"保存到数据库失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def analyze_all_novels(self):
        """分析所有小说"""
        print("开始分析小说风格和背景...")
        
        novel_path = Path(self.novel_base_path)
        for novel_folder in novel_path.iterdir():
            if novel_folder.is_dir() and novel_folder.name != '.gitkeep':
                novel_title = novel_folder.name
                print(f"\n正在分析小说: {novel_title}")
                
                # 读取小说内容
                chapters = self.read_novel_content(novel_folder.name)
                if not chapters:
                    print(f"未找到小说《{novel_title}》的章节内容")
                    continue
                
                # 调用AI分析
                print("正在调用AI分析小说风格...")
                analysis_result = self.call_ai_analysis(novel_title, chapters)
                
                if analysis_result:
                    print("AI分析结果:")
                    print(json.dumps(analysis_result, ensure_ascii=False, indent=2))
                    
                    # 保存到数据库
                    self.save_to_database(novel_title, analysis_result)
                else:
                    print("AI分析失败")
    
    def run(self):
        """运行分析程序"""
        self.analyze_all_novels()
        print("\n分析完成！")

if __name__ == "__main__":
    analyzer = NovelStyleAnalyzer()
    analyzer.run()
