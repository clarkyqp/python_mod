import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from threading import Thread

class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件整理工具")
        self.root.geometry("600x400")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', padding=6, font=('Arial', 10))
        
        # 创建UI元素
        self.create_widgets()
        
        # 初始化日志文本框
        self.log_text = tk.Text(self.root, height=15, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def create_widgets(self):
        # 顶部框架
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 源文件夹选择
        ttk.Label(top_frame, text="源文件夹:").pack(side=tk.LEFT)
        self.source_path = tk.StringVar()
        source_entry = ttk.Entry(top_frame, textvariable=self.source_path, width=40)
        source_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="浏览...", command=self.select_source).pack(side=tk.LEFT)
        
        # 目标文件夹选择
        ttk.Label(top_frame, text="目标文件夹:").pack(side=tk.LEFT, padx=(10,0))
        self.target_path = tk.StringVar()
        target_entry = ttk.Entry(top_frame, textvariable=self.target_path, width=40)
        target_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="浏览...", command=self.select_target).pack(side=tk.LEFT)
        
        # 操作按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 开始按钮
        ttk.Button(button_frame, text="开始整理", command=self.start_moving).pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

    def select_source(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.source_path.set(folder_selected)
            self.log_message(f"已选择源文件夹: {folder_selected}")
            # 自动设置目标文件夹为源文件夹下的"1"文件夹
            default_target = os.path.join(folder_selected, "1")
            self.target_path.set(default_target)

    def select_target(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.target_path.set(folder_selected)
            self.log_message(f"已选择目标文件夹: {folder_selected}")

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def start_moving(self):
        source = self.source_path.get()
        target = self.target_path.get()
        
        if not source:
            messagebox.showwarning("警告", "请先选择源文件夹！")
            return
            
        if not target:
            messagebox.showwarning("警告", "请先选择目标文件夹！")
            return
            
        # 检查源文件夹是否存在
        if not os.path.isdir(source):
            messagebox.showerror("错误", "指定的源文件夹不存在！")
            return
            
        # 检查目标文件夹是否存在，不存在则创建
        if not os.path.exists(target):
            try:
                os.makedirs(target)
                self.log_message(f"创建目标文件夹: {target}")
            except OSError as e:
                messagebox.showerror("错误", f"无法创建目标文件夹: {e}")
                return
        
        # 在新线程中执行文件移动操作
        Thread(target=self.move_files, args=(source, target), daemon=True).start()

    def move_files(self, source_dir, target_dir):
        self.log_message(f"开始整理文件: {source_dir} -> {target_dir}")
        
        # 获取所有文件
        all_files = []
        for root, _, files in os.walk(source_dir):
            # 跳过目标文件夹
            if os.path.abspath(root) == os.path.abspath(target_dir):
                continue
                
            for file in files:
                src_path = os.path.join(root, file)
                all_files.append(src_path)
        
        total_files = len(all_files)
        if total_files == 0:
            self.log_message("没有找到任何文件！")
            return
            
        self.log_message(f"共找到 {total_files} 个文件")
        
        # 处理每个文件
        for i, src_path in enumerate(all_files):
            file_name = os.path.basename(src_path)
            dst_path = os.path.join(target_dir, file_name)
            
            # 处理文件名冲突
            if os.path.exists(dst_path):
                base, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(dst_path):
                    new_name = f"{base}_{counter}{ext}"
                    dst_path = os.path.join(target_dir, new_name)
                    counter += 1
                self.log_message(f"文件 {file_name} 已存在，重命名为 {new_name}")
            
            try:
                shutil.move(src_path, dst_path)
                self.log_message(f"移动: {src_path} -> {dst_path}")
            except Exception as e:
                self.log_message(f"移动文件 {src_path} 失败: {e}")
            
            # 更新进度
            progress = (i + 1) / total_files * 100
            self.update_progress(progress)
        
        # 删除空子文件夹
        self.log_message("开始删除空子文件夹...")
        for root, dirs, _ in os.walk(source_dir, topdown=False):
            # 跳过目标文件夹和源文件夹本身
            if os.path.abspath(root) == os.path.abspath(source_dir) or os.path.abspath(root) == os.path.abspath(target_dir):
                continue
                
            try:
                if not os.listdir(root):  # 检查是否为空文件夹
                    os.rmdir(root)
                    self.log_message(f"删除空文件夹: {root}")
            except OSError as e:
                self.log_message(f"无法删除 {root}: {e}")
        
        self.log_message("文件整理完成！")
        self.update_progress(0)
        messagebox.showinfo("完成", "文件整理完成！")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileMoverApp(root)
    root.mainloop()