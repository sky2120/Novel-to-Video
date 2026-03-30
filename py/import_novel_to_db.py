import os
import json
import pymysql

# 配置文件路径（相对于当前工作目录）
CONFIG_FILE = 'db_config.json'
NOVEL_DIR = 'novel'

def load_config():
    """加载数据库配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_novel_folders(novel_dir):
    """获取所有小说文件夹名称"""
    folders = []
    if os.path.exists(novel_dir):
        for item in os.listdir(novel_dir):
            item_path = os.path.join(novel_dir, item)
            if os.path.isdir(item_path) and item != '.gitkeep':
                folders.append(item)
    return folders

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

def import_novels_to_db(conn, novel_folders):
    """将小说名称插入数据库"""
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        # 查询已存在的小说
        cursor.execute("SELECT title FROM novels")
        existing_novels = {row[0] for row in cursor.fetchall()}
        
        # 插入新小说
        inserted_count = 0
        for title in novel_folders:
            if title not in existing_novels:
                cursor.execute(
                    "INSERT INTO novels (title) VALUES (%s)",
                    (title,)
                )
                inserted_count += 1
        
        conn.commit()
        print(f"成功导入 {inserted_count} 本小说")
        
    except Exception as e:
        print(f"导入失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def main():
    """主函数"""
    print("开始导入小说到数据库...")
    
    # 检查配置文件
    if not os.path.exists(CONFIG_FILE):
        print(f"错误：配置文件 {CONFIG_FILE} 不存在！")
        print("请复制 db_config.example.json 为 db_config.json 并配置数据库信息")
        return
    
    # 加载配置
    config = load_config()
    
    # 获取小说文件夹
    novel_folders = get_novel_folders(NOVEL_DIR)
    if not novel_folders:
        print(f"在 {NOVEL_DIR} 目录下未找到小说文件夹")
        return
    
    print(f"找到 {len(novel_folders)} 本小说")
    
    # 连接数据库并导入
    conn = connect_db(config)
    if conn:
        import_novels_to_db(conn, novel_folders)

if __name__ == "__main__":
    main()