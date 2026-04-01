import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import os
import sys
import threading

class ProgramGUI:
    def __init__(self, master):
        self.master = master
        master.title("AI漫剧程序运行器")
        master.geometry("800x600")
        master.minsize(800, 600)
        
        # 让窗口在屏幕正中间显示
        master.update_idletasks()
        width = master.winfo_width()
        height = master.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (width // 2)
        y = (master.winfo_screenheight() // 2) - (height // 2)
        master.geometry(f"{width}x{height}+{x}+{y}")

        # 创建主框架
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建标题
        title_label = ttk.Label(main_frame, text="AI漫剧程序运行器", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 创建按钮框架
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.BOTH, expand=True)

        # 加载程序列表并创建按钮
        self.load_programs(button_frame)

    def load_programs(self, button_frame):
        # 文件名到中文功能名称的映射
        program_names = {
            'import_novel_to_db': '导入小说到数据库',
            'import_chapters_to_db': '导入章节到数据库',
            'generate_segment_prompts': '生成场景分段提示词',
            'generate_segment_images': '生成场景分段图片',
            'segment_novel_and_generate_prompts': '分段小说生成提示词',
            'analyze_novel_style': '分析小说风格',
            'analyze_novel_characters': '分析小说角色',
            'analyze_frequent_scenes': '分析常用场景',
            'analyze_frequent_items': '分析常用物品',
            'generate_role_images': '生成角色图片',
            'generate_scene_images': '生成场景图片',
            'generate_item_images': '生成物品图片',
            'upload_images_to_server': '上传图片到服务器',
            'check_novels': '检查小说',
            'check_segments': '检查分段',
            'check_image_status': '检查图片状态',
            'check_tables': '检查表',
            'create_chapters_table': '创建章节表',
            'create_segment_table': '创建分段表',
            'update_segment_table': '更新分段表',
            'add_image_url_columns': '添加图片URL列',
            'main': '主程序'
        }
        
        # 按步骤分组的程序列表
        steps = [
            {
                'name': '第一步：数据导入',
                'programs': ['import_novel_to_db', 'import_chapters_to_db', 'generate_segment_prompts', 'generate_segment_images']
            },
            {
                'name': '第二步：小说分析',
                'programs': ['segment_novel_and_generate_prompts', 'analyze_novel_style', 
                           'analyze_novel_characters', 'analyze_frequent_scenes', 'analyze_frequent_items']
            },
            {
                'name': '第三步：图片生成',
                'programs': ['generate_role_images', 'generate_scene_images', 'generate_item_images']
            },
            {
                'name': '第四步：图片上传',
                'programs': ['upload_images_to_server']
            },
            {
                'name': '第五步：数据检查',
                'programs': ['check_novels', 'check_segments', 'check_image_status']
            },
            {
                'name': '第六步：数据库维护',
                'programs': ['check_tables', 'create_chapters_table', 'create_segment_table', 
                           'update_segment_table', 'add_image_url_columns']
            },
            {
                'name': '第七步：主程序',
                'programs': ['main']
            }
        ]
        
        # 创建步骤按钮
        for i, step in enumerate(steps):
            # 创建步骤按钮
            button = ttk.Button(button_frame, text=step['name'],
                               command=lambda s=step: self.open_step_window(s, program_names))
            button.pack(fill=tk.X, pady=5)

    def open_step_window(self, step, program_names):
        # 创建新窗口
        step_window = tk.Toplevel(self.master)
        step_window.title(step['name'])
        step_window.geometry("800x600")
        step_window.minsize(800, 600)
        
        # 让窗口在屏幕正中间显示
        step_window.update_idletasks()
        width = step_window.winfo_width()
        height = step_window.winfo_height()
        x = (step_window.winfo_screenwidth() // 2) - (width // 2)
        y = (step_window.winfo_screenheight() // 2) - (height // 2)
        step_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 创建主框架
        main_frame = ttk.Frame(step_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text=step['name'], font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # 创建左右分栏布局
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：功能按钮区域
        left_frame = ttk.Frame(content_frame, padding="10")
        left_frame.pack(fill=tk.Y, side=tk.LEFT)
        
        # 创建功能按钮
        for i, program_name in enumerate(step['programs']):
            filename = f"{program_name}.py"
            current_dir = os.path.dirname(os.path.abspath(__file__))
            python_files = [f for f in os.listdir(current_dir) if f.endswith('.py') and f != 'gui.py']
            if filename in python_files:
                display_name = program_names.get(program_name, program_name)
                button = ttk.Button(left_frame, text=display_name,
                                   command=lambda f=filename, w=step_window: self.run_program(f, w))
                button.pack(fill=tk.X, pady=5)
        
        # 右侧：程序输出区域
        right_frame = ttk.Frame(content_frame, padding="10")
        right_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        output_label = ttk.Label(right_frame, text="程序输出：", font=("Arial", 12, "bold"))
        output_label.pack(anchor=tk.W)
        
        # 创建输出文本框并存储到窗口对象上
        step_window.output_text = scrolledtext.ScrolledText(right_frame, height=20, wrap=tk.WORD)
        step_window.output_text.pack(fill=tk.BOTH, expand=True)

    def run_program(self, filename, window):
        def run():
            try:
                # 清空输出文本框
                window.output_text.delete(1.0, tk.END)
                window.output_text.insert(tk.END, f"开始运行程序: {filename}\n")
                
                # 运行Python程序
                # 获取项目根目录（py目录的上一级）
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                process = subprocess.Popen(
                    [sys.executable, os.path.join('py', filename)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_root
                )
                
                # 读取输出
                stdout, stderr = process.communicate()
                
                if stdout:
                    window.output_text.insert(tk.END, stdout)
                if stderr:
                    window.output_text.insert(tk.END, f"错误信息:\n{stderr}")
                
                window.output_text.insert(tk.END, f"\n程序完成: {filename}")
            except Exception as e:
                window.output_text.insert(tk.END, f"运行出错: {str(e)}\n")

        # 在新线程中运行程序，避免阻塞GUI
        thread = threading.Thread(target=run)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    print("启动GUI程序...")
    root = tk.Tk()
    print("创建主窗口成功")
    app = ProgramGUI(root)
    print("创建程序实例成功")
    print("进入主循环...")
    root.mainloop()
    print("程序退出")