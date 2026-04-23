import os
import zipfile
import rarfile
import py7zr
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ArchiveExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("压缩包解压工具")
        self.root.geometry("500x300")
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure('TButton', padding=6)
        self.style.configure('TLabel', padding=6, font=('Arial', 10))
        
        # 创建UI元素
        self.create_widgets()
        
        # 初始化日志文本框
        self.log_text = tk.Text(self.root, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 检查依赖库
        self.check_dependencies()

    def create_widgets(self):
        # 顶部框架
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 文件夹选择按钮
        select_button = ttk.Button(top_frame, text="选择文件夹", command=self.select_folder)
        select_button.pack(side=tk.LEFT)
        
        # 文件夹路径显示
        self.folder_path = tk.StringVar()
        path_label = ttk.Label(top_frame, textvariable=self.folder_path, relief=tk.SUNKEN)
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 开始按钮
        start_button = ttk.Button(top_frame, text="开始解压", command=self.start_extraction)
        start_button.pack(side=tk.RIGHT)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.log_message(f"已选择文件夹: {folder_selected}")

    def start_extraction(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("警告", "请先选择文件夹！")
            return
            
        if not os.path.isdir(folder):
            messagebox.showerror("错误", "指定的文件夹不存在！")
            return
            
        # 在新线程中执行解压操作
        Thread(target=self.process_folder, args=(folder,), daemon=True).start()

    def log_message(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update_idletasks()

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def check_dependencies(self):
        try:
            import rarfile
        except ImportError:
            self.log_message("警告: rarfile 模块未安装，将无法处理RAR文件")
            
        try:
            import py7zr
        except ImportError:
            self.log_message("警告: py7zr 模块未安装，将无法处理7z文件")

    def create_unique_folder(self, base_path):
        counter = 1
        new_path = base_path
        while os.path.exists(new_path):
            new_path = f"{base_path}_{counter}"
            counter += 1
        os.makedirs(new_path)
        return new_path

    def extract_zip(self, zip_path, extract_to):
        try:
            folder_name = os.path.splitext(os.path.basename(zip_path))[0]
            target_folder = os.path.join(extract_to, folder_name)
            target_folder = self.create_unique_folder(target_folder)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_folder)
            os.remove(zip_path)
            self.log_message(f"解压并删除成功: {zip_path} -> {target_folder}")
        except Exception as e:
            self.log_message(f"处理ZIP文件 {zip_path} 时出错: {e}")

    def extract_rar(self, rar_path, extract_to):
        try:
            folder_name = os.path.splitext(os.path.basename(rar_path))[0]
            target_folder = os.path.join(extract_to, folder_name)
            target_folder = self.create_unique_folder(target_folder)
            
            with rarfile.RarFile(rar_path, 'r') as rar_ref:
                rar_ref.extractall(target_folder)
            os.remove(rar_path)
            self.log_message(f"解压并删除成功: {rar_path} -> {target_folder}")
        except Exception as e:
            self.log_message(f"处理RAR文件 {rar_path} 时出错: {e}")

    def extract_7z(self, sevenz_path, extract_to):
        try:
            folder_name = os.path.splitext(os.path.basename(sevenz_path))[0]
            target_folder = os.path.join(extract_to, folder_name)
            target_folder = self.create_unique_folder(target_folder)
            
            with py7zr.SevenZipFile(sevenz_path, mode='r') as sevenz_ref:
                sevenz_ref.extractall(target_folder)
            os.remove(sevenz_path)
            self.log_message(f"解压并删除成功: {sevenz_path} -> {target_folder}")
        except Exception as e:
            self.log_message(f"处理7Z文件 {sevenz_path} 时出错: {e}")

    def process_compressed_file(self, file_path, folder_path):
        if file_path.lower().endswith('.zip'):
            self.extract_zip(file_path, folder_path)
        elif file_path.lower().endswith('.rar'):
            self.extract_rar(file_path, folder_path)
        elif file_path.lower().endswith('.7z'):
            self.extract_7z(file_path, folder_path)

    def process_folder(self, root_folder):
        self.log_message(f"开始处理文件夹: {root_folder}")
        
        # 获取所有压缩文件
        compressed_files = []
        for foldername, _, filenames in os.walk(root_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                if any(file_path.lower().endswith(ext) for ext in ['.zip', '.rar', '.7z']):
                    compressed_files.append((file_path, foldername))
        
        total_files = len(compressed_files)
        if total_files == 0:
            self.log_message("没有找到任何压缩文件！")
            return
            
        self.log_message(f"共找到 {total_files} 个压缩文件")
        
        # 处理每个文件
        for i, (file_path, folder_path) in enumerate(compressed_files):
            self.log_message(f"正在处理: {file_path}")
            self.process_compressed_file(file_path, folder_path)
            progress = (i + 1) / total_files * 100
            self.update_progress(progress)
        
        self.log_message("处理完成！")
        self.update_progress(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ArchiveExtractorApp(root)
    root.mainloop()