"""
程序名称：检查图片状态并更新数据库
功能描述：检测数据库中标记为已生成的图片是否在本地文件夹中存在，如果不存在就更新为未生成状态
作者：AI Assistant
日期：2026-03-31
"""
import os
import json
import pymysql

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'
IMAGES_DIR = 'images'

def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def check_character_images(conn, novel_id, novel_title):
    """检查角色图片是否存在"""
    cursor = conn.cursor()
    try:
        # 获取所有已生成的角色
        cursor.execute("""
            SELECT id, name FROM characters 
            WHERE novel_id = %s AND is_generated = TRUE
        """, (novel_id,))
        characters = cursor.fetchall()
        
        updated_count = 0
        
        # 检查每个角色的图片
        for character_id, name in characters:
            novel_dir = os.path.join(IMAGES_DIR, novel_title)
            
            # 检查是否存在角色的图片文件（新格式：从数据库获取路径）
            has_images = False
            
            # 从数据库获取角色的图片路径
            cursor.execute("""
                SELECT face_image_front, face_image_side, face_image_half 
                FROM characters 
                WHERE id = %s
            """, (character_id,))
            image_paths = cursor.fetchone()
            
            if image_paths:
                face_image_front, face_image_side, face_image_half = image_paths
                # 检查任何一个图片路径是否存在
                if (face_image_front and os.path.exists(face_image_front)) or \
                   (face_image_side and os.path.exists(face_image_side)) or \
                   (face_image_half and os.path.exists(face_image_half)):
                    has_images = True
            
            # 如果没有找到图片，更新状态为未生成
            if not has_images:
                cursor.execute("""
                    UPDATE characters 
                    SET is_generated = FALSE 
                    WHERE id = %s
                """, (character_id,))
                updated_count += 1
                print(f"更新角色状态: {name} (ID={character_id}) -> 未生成")
        
        conn.commit()
        return updated_count
        
    except Exception as e:
        print(f"检查角色图片失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()

def check_scene_images(conn, novel_id, novel_title):
    """检查场景图片是否存在"""
    cursor = conn.cursor()
    try:
        # 获取所有已生成的场景
        cursor.execute("""
            SELECT id, name FROM scenes 
            WHERE novel_id = %s AND is_generated = TRUE
        """, (novel_id,))
        scenes = cursor.fetchall()
        
        updated_count = 0
        
        # 检查每个场景的图片
        for scene_id, name in scenes:
            novel_dir = os.path.join(IMAGES_DIR, novel_title)
            
            # 检查是否存在场景的图片文件（新格式：从数据库获取路径）
            has_image = False
            
            # 从数据库获取场景的图片路径
            cursor.execute("""
                SELECT image_url 
                FROM scenes 
                WHERE id = %s
            """, (scene_id,))
            image_path = cursor.fetchone()
            
            if image_path and image_path[0] and os.path.exists(image_path[0]):
                has_image = True
            
            # 如果没有找到图片，更新状态为未生成
            if not has_image:
                cursor.execute("""
                    UPDATE scenes 
                    SET is_generated = FALSE 
                    WHERE id = %s
                """, (scene_id,))
                updated_count += 1
                print(f"更新场景状态: {name} (ID={scene_id}) -> 未生成")
        
        conn.commit()
        return updated_count
        
    except Exception as e:
        print(f"检查场景图片失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()

def check_item_images(conn, novel_id, novel_title):
    """检查物品图片是否存在"""
    cursor = conn.cursor()
    try:
        # 获取所有已生成的物品
        cursor.execute("""
            SELECT id, name FROM items 
            WHERE novel_id = %s AND is_generated = TRUE
        """, (novel_id,))
        items = cursor.fetchall()
        
        updated_count = 0
        
        # 检查每个物品的图片
        for item_id, name in items:
            novel_dir = os.path.join(IMAGES_DIR, novel_title)
            
            # 检查是否存在物品的图片文件（新格式：从数据库获取路径）
            has_image = False
            
            # 从数据库获取物品的图片路径
            cursor.execute("""
                SELECT image_url 
                FROM items 
                WHERE id = %s
            """, (item_id,))
            image_path = cursor.fetchone()
            
            if image_path and image_path[0] and os.path.exists(image_path[0]):
                has_image = True
            
            # 如果没有找到图片，更新状态为未生成
            if not has_image:
                cursor.execute("""
                    UPDATE items 
                    SET is_generated = FALSE 
                    WHERE id = %s
                """, (item_id,))
                updated_count += 1
                print(f"更新物品状态: {name} (ID={item_id}) -> 未生成")
        
        conn.commit()
        return updated_count
        
    except Exception as e:
        print(f"检查物品图片失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始检查图片状态并更新数据库...")
    
    # 加载配置
    config = load_config()
    
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
    
    total_updated = 0
    
    # 处理每本小说
    for novel_id, novel_title in novels:
        print(f"\n正在检查小说: {novel_title}")
        
        # 检查角色图片
        character_updated = check_character_images(conn, novel_id, novel_title)
        total_updated += character_updated
        
        # 检查场景图片
        scene_updated = check_scene_images(conn, novel_id, novel_title)
        total_updated += scene_updated
        
        # 检查物品图片
        item_updated = check_item_images(conn, novel_id, novel_title)
        total_updated += item_updated
    
    conn.close()
    print(f"\n检查完成！总共更新了 {total_updated} 条记录")

if __name__ == "__main__":
    main()
