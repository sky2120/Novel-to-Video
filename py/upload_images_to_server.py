#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：图片上传服务器
功能描述：将所有生成的图片上传到图片服务器，并将URL存储到数据库
作者：AI Assistant
日期：2026-03-31
"""

import os
import json
import pymysql
import requests
import re

# 配置文件路径（相对于项目根目录）
CONFIG_FILE = 'config.json'
IMAGES_DIR = 'images'


def load_config():
    """加载配置"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# 加载配置
config = load_config()
SERVER_URL = config['server']['image_server_url']


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


def get_server_images():
    """获取服务器上所有图片列表"""
    url = f"{SERVER_URL}/images"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            images = response.json()
            # 提取所有文件名
            server_filenames = [image['filename'] for image in images]
            print(f"服务器上共有 {len(server_filenames)} 个图片文件")
            return server_filenames
        else:
            print(f"获取服务器图片列表失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"获取服务器图片列表失败: {e}")
        return []


def upload_image(image_path, server_filenames):
    """上传图片到服务器"""
    url = f"{SERVER_URL}/upload"
    
    try:
        # 获取文件扩展名并设置正确的Content-Type
        ext = os.path.splitext(image_path)[1].lower()
        content_type = 'image/jpeg'
        if ext == '.png':
            content_type = 'image/png'
        elif ext == '.gif':
            content_type = 'image/gif'
        elif ext == '.webp':
            content_type = 'image/webp'
        
        # 打开文件并上传，添加正确的Content-Type
        with open(image_path, 'rb') as f:
            files = {'image': (os.path.basename(image_path), f, content_type)}
            response = requests.post(url, files=files)
        
        print(f"上传图片 {image_path}，状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # 解析JSON响应
                result = response.json()
                if result.get('success'):
                    file_info = result.get('file', {})
                    filename = file_info.get('filename')
                    if filename:
                        image_url = f"{SERVER_URL}/uploads/{filename}"
                        print(f"上传成功，图片URL: {image_url}")
                        return image_url
                    else:
                        print("响应中没有文件名信息")
                        return None
                else:
                    print(f"上传失败: {result.get('error', '未知错误')}")
                    return None
            except json.JSONDecodeError:
                # 如果不是JSON格式，尝试从HTML中提取
                html_content = response.text
                print(f"响应内容预览: {html_content[:200]}...")
                
                # 尝试多种方式提取文件名
                filename_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-\d{3}Z\.\w+)', html_content)
                
                if not filename_match:
                    filename_match = re.search(r'([\w-]+\.(jpg|jpeg|png|gif|webp))', html_content)
                
                if filename_match:
                    filename = filename_match.group(1)
                    image_url = f"{SERVER_URL}/uploads/{filename}"
                    print(f"上传成功，图片URL: {image_url}")
                    return image_url
                else:
                    print("无法从响应中提取文件名")
                    return None
        else:
            print(f"上传失败: {response.text[:500]}")  # 只打印前500个字符
            return None
            
    except Exception as e:
        print(f"上传图片失败: {e}")
        return None


def update_character_image_url(conn, character_id, image_url, angle_type):
    """更新角色图片URL到数据库"""
    if not conn or not image_url:
        return False
    
    cursor = conn.cursor()
    try:
        # 根据角度类型更新对应的字段
        if angle_type == "标准脸1":
            field = "face_image_front"
        elif angle_type == "标准脸2":
            field = "face_image_side"
        elif angle_type == "标准脸3":
            field = "face_image_half"
        else:
            return False
        
        cursor.execute(f"""
            UPDATE characters 
            SET {field} = %s 
            WHERE id = %s
        """, (image_url, character_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新角色图片URL失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def update_scene_image_url(conn, scene_id, image_url):
    """更新场景图片URL到数据库"""
    if not conn or not image_url:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE scenes 
            SET image_url = %s 
            WHERE id = %s
        """, (image_url, scene_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新场景图片URL失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def update_item_image_url(conn, item_id, image_url):
    """更新物品图片URL到数据库"""
    if not conn or not image_url:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE items 
            SET image_url = %s 
            WHERE id = %s
        """, (image_url, item_id))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"更新物品图片URL失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()


def process_novel_images(conn, novel_id, novel_title, server_filenames):
    """处理单个小说的图片上传"""
    novel_dir = os.path.join(IMAGES_DIR, novel_title)
    
    if not os.path.exists(novel_dir):
        print(f"小说目录不存在: {novel_dir}")
        return
    
    cursor = conn.cursor()
    
    try:
        # 从数据库获取角色图片路径
        cursor.execute("""
            SELECT id, name, face_image_front, face_image_side, face_image_half 
            FROM characters 
            WHERE novel_id = %s
        """, (novel_id,))
        characters = cursor.fetchall()
        
        # 从数据库获取场景图片路径
        cursor.execute("""
            SELECT id, name, image_url 
            FROM scenes 
            WHERE novel_id = %s
        """, (novel_id,))
        scenes = cursor.fetchall()
        
        # 从数据库获取物品图片路径
        cursor.execute("""
            SELECT id, name, image_url 
            FROM items 
            WHERE novel_id = %s
        """, (novel_id,))
        items = cursor.fetchall()
        
    finally:
        cursor.close()
    
    print(f"找到 {len(characters)} 个角色，{len(scenes)} 个场景，{len(items)} 个物品")
    
    # 处理角色图片
    for character_id, name, face_image_front, face_image_side, face_image_half in characters:
        # 上传正面图片
        if face_image_front and os.path.exists(face_image_front):
            image_url = upload_image(face_image_front, server_filenames)
            if image_url:
                update_character_image_url(conn, character_id, image_url, "标准脸1")
        
        # 上传侧面图片
        if face_image_side and os.path.exists(face_image_side):
            image_url = upload_image(face_image_side, server_filenames)
            if image_url:
                update_character_image_url(conn, character_id, image_url, "标准脸2")
        
        # 上传半侧面图片
        if face_image_half and os.path.exists(face_image_half):
            image_url = upload_image(face_image_half, server_filenames)
            if image_url:
                update_character_image_url(conn, character_id, image_url, "标准脸3")
    
    # 处理场景图片
    for scene_id, name, image_path in scenes:
        if image_path and os.path.exists(image_path):
            image_url = upload_image(image_path, server_filenames)
            if image_url:
                update_scene_image_url(conn, scene_id, image_url)
    
    # 处理物品图片
    for item_id, name, image_path in items:
        if image_path and os.path.exists(image_path):
            image_url = upload_image(image_path, server_filenames)
            if image_url:
                update_item_image_url(conn, item_id, image_url)


def main():
    """主函数"""
    print("开始上传图片到服务器...")
    
    # 获取服务器上已有的图片列表
    server_filenames = get_server_images()
    
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
    
    # 处理每本小说的图片
    for novel_id, novel_title in novels:
        print(f"\n正在处理小说: {novel_title}")
        process_novel_images(conn, novel_id, novel_title, server_filenames)
    
    conn.close()
    print("\n图片上传完成！")


if __name__ == "__main__":
    main()