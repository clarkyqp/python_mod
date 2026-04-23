import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class ExtensionConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("文件扩展名转换器(支持子文件夹)")
        self.root.geometry("450x300")
        
        # 默认设置
        self.source_ext = ".m"
        self.target_ext = ".txt"
        self.include_subfolders = tk.BooleanVar(value=True)  # 默认包含子文件夹
        
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        tk.Label(self.root, text="文件扩展名批量转换工具", font=('Arial', 12), pady=10).pack()
        
        # 扩展名选择框架
        ext_frame = tk.Frame(self.root)
        ext_frame.pack(pady=10)
        
        # 源扩展名选择
        tk.Label(ext_frame, text="源扩展名:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.source_var = tk.StringVar(value=self.source_ext)
        source_entry = tk.Entry(ext_frame, textvariable=self.source_var, width=10)
        source_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        # 目标扩展名选择
        tk.Label(ext_frame, text="目标扩展名:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.target_var = tk.StringVar(value=self.target_ext)
        target_entry = tk.Entry(ext_frame, textvariable=self.target_var, width=10)
        target_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 预设按钮
        preset_frame = tk.Frame(self.root)
        preset_frame.pack(pady=5)
        
        tk.Button(preset_frame, text=".m → .txt", command=lambda: self.set_extensions(".m", ".txt")).pack(side=tk.LEFT, padx=5)
        tk.Button(preset_frame, text=".txt → .m", command=lambda: self.set_extensions(".txt", ".m")).pack(side=tk.LEFT, padx=5)
        
        # 子文件夹选项
        subfolder_frame = tk.Frame(self.root)
        subfolder_frame.pack(pady=10)
        tk.Checkbutton(subfolder_frame, text="包含子文件夹", variable=self.include_subfolders).pack()
        
        # 选择文件夹按钮
        tk.Button(self.root, text="选择文件夹并转换", command=self.select_and_convert, 
                 padx=20, pady=10, bg="#4CAF50", fg="white").pack(pady=15)
    
    def set_extensions(self, source, target):
        """设置预设的扩展名"""
        self.source_var.set(source)
        self.target_var.set(target)
    
    def select_and_convert(self):
        """选择文件夹并执行转换"""
        folder_path = filedialog.askdirectory(title="选择要转换的文件夹")
        if folder_path:
            self.source_ext = self.source_var.get().strip()
            self.target_ext = self.target_var.get().strip()
            
            # 验证扩展名格式
            if not self.source_ext.startswith("."):
                self.source_ext = "." + self.source_ext
            if not self.target_ext.startswith("."):
                self.target_ext = "." + self.target_ext
                
            self.convert_files(folder_path)
    
    def convert_files(self, folder_path):
        """执行文件扩展名转换"""
        converted_count = 0
        skipped_count = 0
        processed_folders = 0
        
        # 遍历文件系统
        for root, dirs, files in os.walk(folder_path):
            processed_folders += 1
            for filename in files:
                file_path = os.path.join(root, filename)
                name, ext = os.path.splitext(filename)
                ext = ext.lower()
                
                # 只转换匹配源扩展名的文件
                if ext == self.source_ext.lower():
                    new_filename = name + self.target_ext
                    new_path = os.path.join(root, new_filename)
                    
                    # 检查目标文件是否已存在
                    if os.path.exists(new_path):
                        skipped_count += 1
                        continue
                        
                    os.rename(file_path, new_path)
                    converted_count += 1
            
            # 如果不包含子文件夹，只处理第一层就退出
            if not self.include_subfolders.get():
                break
        
        # 显示结果
        result = (
            f"转换完成！\n\n"
            f"转换设置: {self.source_ext} → {self.target_ext}\n"
            f"扫描文件夹: {processed_folders} 个\n"
            f"已转换文件: {converted_count} 个\n"
            f"跳过文件(目标已存在): {skipped_count} 个"
        )
        messagebox.showinfo("转换结果", result)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtensionConverter(root)
    root.mainloop()