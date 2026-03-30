import os
import re
import pymysql
from pathlib import Path

class NovelImporter:
    def __init__(self):
        # 从配置文件读取数据库连接信息
        self.db_config = self._load_db_config()
        self.novel_base_path = r'd:\桌面\临时文件\A自动生成类型文件\AI漫剧\novel'
    
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
    
    def extract_chapter_number(self, filename):
        """从文件名提取章节编号"""
        # 匹配"第一章.txt"、"第1章.txt"、"001.txt"等格式
        match = re.search(r'第?(\d+)[章话回]?', filename)
        if match:
            return int(match.group(1))
        match = re.search(r'^(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0
    
    def import_novels(self):
        """导入所有小说到数据库"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # 遍历小说文件夹
            novel_path = Path(self.novel_base_path)
            for novel_folder in novel_path.iterdir():
                if novel_folder.is_dir():
                    novel_title = novel_folder.name
                    print(f"正在处理小说: {novel_title}")
                    
                    # 检查是否存在同名小说
                    cursor.execute("SELECT id FROM novels WHERE title = %s", (novel_title,))
                    existing_novel = cursor.fetchone()
                    
                    if existing_novel:
                        novel_id = existing_novel[0]
                        print(f"  小说已存在，ID: {novel_id}")
                    else:
                        # 检查是否有其他标题但文件夹路径匹配的记录
                        # 这里简化处理，直接创建新记录
                        novel_sql = """
                        INSERT INTO novels (title, status) 
                        VALUES (%s, 'ongoing')
                        """
                        cursor.execute(novel_sql, (novel_title,))
                        conn.commit()
                        novel_id = cursor.lastrowid
                        print(f"  创建新小说记录，ID: {novel_id}")
                    
                    # 遍历章节文件
                    chapters = []
                    for chapter_file in novel_folder.iterdir():
                        if chapter_file.is_file() and chapter_file.suffix == '.txt':
                            chapter_number = self.extract_chapter_number(chapter_file.name)
                            chapter_title = chapter_file.stem
                            
                            # 读取章节内容
                            try:
                                with open(chapter_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                word_count = len(content.strip())
                                
                                chapters.append({
                                    'novel_id': novel_id,
                                    'chapter_number': chapter_number,
                                    'title': chapter_title,
                                    'content': content,
                                    'word_count': word_count
                                })
                                print(f"  读取章节: {chapter_title}")
                            except Exception as e:
                                print(f"  读取文件失败: {chapter_file.name}, 错误: {e}")
                    
                    # 按章节编号排序
                    chapters.sort(key=lambda x: x['chapter_number'])
                    
                    # 插入章节信息
                    for chapter in chapters:
                        chapter_sql = """
                        INSERT INTO chapters (novel_id, chapter_number, title, content, word_count)
                        VALUES (%(novel_id)s, %(chapter_number)s, %(title)s, %(content)s, %(word_count)s)
                        ON DUPLICATE KEY UPDATE 
                            title = %(title)s, 
                            content = %(content)s, 
                            word_count = %(word_count)s,
                            updated_at = CURRENT_TIMESTAMP
                        """
                        cursor.execute(chapter_sql, chapter)
                    
                    # 更新小说总章节数
                    cursor.execute("""
                    UPDATE novels 
                    SET total_chapters = (SELECT COUNT(*) FROM chapters WHERE novel_id = %s)
                    WHERE id = %s
                    """, (novel_id, novel_id))
                    
                    conn.commit()
                    print(f"小说 {novel_title} 导入完成，共 {len(chapters)} 章节\n")
                    
        except Exception as e:
            print(f"导入过程出错: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def update_novel_title(self, old_title, new_title):
        """更新小说标题"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # 更新小说标题
            update_sql = "UPDATE novels SET title = %s WHERE title = %s"
            cursor.execute(update_sql, (new_title, old_title))
            
            if cursor.rowcount > 0:
                print(f"成功将小说 '{old_title}' 重命名为 '{new_title}'")
            else:
                print(f"未找到小说 '{old_title}'")
            
            conn.commit()
        except Exception as e:
            print(f"更新小说标题失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def run(self):
        """运行导入程序"""
        print("开始导入小说到数据库...")
        self.import_novels()
        print("导入完成！")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='导入小说到数据库或更新小说标题')
    parser.add_argument('--update-title', nargs=2, metavar=('OLD_TITLE', 'NEW_TITLE'),
                       help='更新小说标题')
    
    args = parser.parse_args()
    
    importer = NovelImporter()
    
    if args.update_title:
        old_title, new_title = args.update_title
        importer.update_novel_title(old_title, new_title)
    else:
        importer.run()
