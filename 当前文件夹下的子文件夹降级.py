import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件整理工具")
        self.root.geometry("600x400")
        
        # 创建UI元素
        self.create_widgets()
        
    def create_widgets(self):
        # 文件夹选择部分
        frame_folder = tk.LabelFrame(self.root, text="选择文件夹", padx=10, pady=10)
        frame_folder.pack(pady=10, padx=10, fill="x")
        
        self.folder_path = tk.StringVar()
        tk.Entry(frame_folder, textvariable=self.folder_path, width=50).pack(side="left", padx=5)
        tk.Button(frame_folder, text="浏览...", command=self.select_folder).pack(side="left")
        
        # 操作选项部分
        frame_options = tk.LabelFrame(self.root, text="操作选项", padx=10, pady=10)
        frame_options.pack(pady=10, padx=10, fill="x")
        
        self.move_files_var = tk.BooleanVar(value=True)
        self.delete_password_var = tk.BooleanVar(value=True)
        self.delete_empty_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(frame_options, text="移动深层文件到直接子文件夹", variable=self.move_files_var).pack(anchor="w")
        tk.Checkbutton(frame_options, text="删除所有PassWord.txt文件", variable=self.delete_password_var).pack(anchor="w")
        tk.Checkbutton(frame_options, text="删除所有空文件夹", variable=self.delete_empty_var).pack(anchor="w")
        
        # 执行按钮
        tk.Button(self.root, text="执行操作", command=self.execute_operations, bg="#4CAF50", fg="white").pack(pady=20)
        
        # 日志输出
        frame_log = tk.LabelFrame(self.root, text="操作日志", padx=10, pady=10)
        frame_log.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_text = tk.Text(frame_log, height=10)
        self.log_text.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def move_files_to_parent(self, current_dir):
        """将深层子文件夹中的文件移动到直接子文件夹"""
        moved_files = 0
        for root, dirs, files in os.walk(current_dir):
            relative_path = os.path.relpath(root, current_dir)
            path_parts = relative_path.split(os.sep)
            
            if len(path_parts) > 1:  # 只在深层子文件夹操作
                target_dir = os.path.join(current_dir, path_parts[0])
                
                for file in files:
                    src = os.path.join(root, file)
                    dst = os.path.join(target_dir, file)
                    
                    # 处理文件名冲突
                    counter = 1
                    while os.path.exists(dst):
                        name, ext = os.path.splitext(file)
                        dst = os.path.join(target_dir, f"{name}_{counter}{ext}")
                        counter += 1
                    
                    try:
                        shutil.move(src, dst)
                        moved_files += 1
                        self.log_message(f"移动文件: {src} -> {dst}")
                    except Exception as e:
                        self.log_message(f"移动失败 {src}: {e}")
        
        return moved_files
    
    def delete_password_files(self, directory):
        """删除所有PassWord.txt文件"""
        deleted = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower() == "查看解压密码.txt":  # 不区分大小写
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        deleted += 1
                        self.log_message(f"删除文件: {file_path}")
                    except Exception as e:
                        self.log_message(f"删除失败 {file_path}: {e}")
        return deleted
    
    def delete_empty_dirs(self, directory):
        """删除所有空文件夹"""
        deleted = 0
        for root, dirs, files in os.walk(directory, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                try:
                    if not os.listdir(dir_path):  # 检查是否为空
                        os.rmdir(dir_path)
                        deleted += 1
                        self.log_message(f"删除空文件夹: {dir_path}")
                except Exception as e:
                    self.log_message(f"删除失败 {dir_path}: {e}")
        return deleted
    
    def execute_operations(self):
        target_dir = self.folder_path.get()
        if not target_dir:
            messagebox.showerror("错误", "请先选择文件夹")
            return
            
        if not messagebox.askyesno("确认", "确定要执行所选操作吗？操作不可逆！"):
            return
            
        self.log_text.delete(1.0, tk.END)
        self.log_message("开始执行操作...")
        
        total_moved = 0
        total_deleted_files = 0
        total_deleted_dirs = 0
        
        try:
            if self.move_files_var.get():
                self.log_message("\n正在移动文件...")
                total_moved = self.move_files_to_parent(target_dir)
                
            if self.delete_password_var.get():
                self.log_message("\n正在删除PassWord.txt文件...")
                total_deleted_files = self.delete_password_files(target_dir)
                
            if self.delete_empty_var.get():
                self.log_message("\n正在删除空文件夹...")
                total_deleted_dirs = self.delete_empty_dirs(target_dir)
                
            self.log_message("\n操作完成:")
            self.log_message(f"- 移动文件数量: {total_moved}")
            self.log_message(f"- 删除PassWord.txt文件数量: {total_deleted_files}")
            self.log_message(f"- 删除空文件夹数量: {total_deleted_dirs}")
            
            messagebox.showinfo("完成", "所有操作执行完毕")
            
        except Exception as e:
            self.log_message(f"\n发生错误: {str(e)}")
            messagebox.showerror("错误", f"执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()