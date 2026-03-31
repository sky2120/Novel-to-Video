#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序名称：AI漫剧主程序
功能描述：按照小说导入 → 内容分析 → 资源提取 → 图像生成的顺序依次运行各个脚本
作者：AI Assistant
日期：2026-03-31
"""

import subprocess
import sys
import os

# 获取脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name):
    """运行指定的脚本"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    
    if not os.path.exists(script_path):
        print(f"错误：脚本文件 {script_name} 不存在")
        return False
    
    print(f"\n{'='*60}")
    print(f"开始运行：{script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(SCRIPT_DIR),  # 在项目根目录运行
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("脚本运行成功！")
        print("输出：")
        print(result.stdout)
        
        if result.stderr:
            print("\n警告信息：")
            print(result.stderr)
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"脚本运行失败，退出码：{e.returncode}")
        print("错误输出：")
        print(e.stderr)
        return False
    except Exception as e:
        print(f"运行脚本时发生错误：{e}")
        return False


def run_script_with_check(script_name, skip_keyword):
    """运行脚本并检查是否需要跳过"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    
    if not os.path.exists(script_path):
        print(f"错误：脚本文件 {script_name} 不存在")
        return False, False
    
    print(f"\n{'='*60}")
    print(f"开始运行：{script_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(SCRIPT_DIR),
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("脚本运行成功！")
        print("输出：")
        print(result.stdout)
        
        if result.stderr:
            print("\n警告信息：")
            print(result.stderr)
            
        # 检查是否需要跳过后续步骤
        needs_processing = skip_keyword not in result.stdout
        return True, needs_processing
        
    except subprocess.CalledProcessError as e:
        print(f"脚本运行失败，退出码：{e.returncode}")
        print("错误输出：")
        print(e.stderr)
        return False, False
    except Exception as e:
        print(f"运行脚本时发生错误：{e}")
        return False, False

def main():
    """主函数"""
    print("AI漫剧自动处理流程开始")
    print("流程：小说导入 → 内容分析 → 资源提取 → 图像生成")
    print()
    
    # 步骤1：小说导入
    if not run_script("import_novel_to_db.py"):
        print("\n小说导入失败，流程终止")
        return
    
    # 步骤2：内容分析
    success, needs_analysis = run_script_with_check("analyze_novel_style.py", "没有待分析的小说")
    if not success:
        print("\n内容分析失败，流程终止")
        return
    
    # 步骤3：资源提取（只有在需要分析时才执行）
    if needs_analysis:
        # 角色提取
        if not run_script("analyze_novel_characters.py"):
            print("\n角色提取失败，流程终止")
            return
        
        # 物品提取
        if not run_script("analyze_frequent_items.py"):
            print("\n物品提取失败，流程终止")
            return
        
        # 场景提取
        if not run_script("analyze_frequent_scenes.py"):
            print("\n场景提取失败，流程终止")
            return
    
    # 步骤4：图像生成
    # 角色图像生成
    success, _ = run_script_with_check("generate_role_images.py", "没有找到未生成的角色")
    
    # 场景图像生成
    success, _ = run_script_with_check("generate_scene_images.py", "没有找到未生成的场景")
    
    # 物品图像生成
    success, _ = run_script_with_check("generate_item_images.py", "没有找到未生成的物品")
    
    print("\n" + "="*60)
    print("🎉 AI漫剧自动处理流程完成！")
    print("所有步骤都已成功执行")
    print("="*60)


if __name__ == "__main__":
    main()
