import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class BCFileCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(".bc! 文件清理工具")
        self.root.geometry("600x400")
        
        # 设置主题风格
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.create_widgets()
    
    def create_widgets(self):
        # 标题
        title_label = ttk.Label(
            self.root, 
            text=".bc! 文件清理工具", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # 说明文字
        desc_label = ttk.Label(
            self.root,
            text="此工具用于删除指定目录及其子目录中所有以.bc!为后缀的文件",
            wraplength=550
        )
        desc_label.pack(pady=5)
        
        # 选择目录框架
        dir_frame = ttk.Frame(self.root)
        dir_frame.pack(pady=15, fill=tk.X, padx=20)
        
        ttk.Label(dir_frame, text="目标目录:").pack(side=tk.LEFT)
        
        self.dir_entry = ttk.Entry(dir_frame)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = ttk.Button(
            dir_frame, 
            text="浏览...", 
            command=self.browse_directory
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # 选项框架
        option_frame = ttk.Frame(self.root)
        option_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_cb = ttk.Checkbutton(
            option_frame,
            text="包含子目录",
            variable=self.recursive_var
        )
        recursive_cb.pack(side=tk.LEFT)
        
        # 操作按钮框架
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=15)
        
        clean_btn = ttk.Button(
            btn_frame,
            text="开始清理",
            command=self.clean_files
        )
        clean_btn.pack(side=tk.LEFT, padx=10)
        
        exit_btn = ttk.Button(
            btn_frame,
            text="退出",
            command=self.root.quit
        )
        exit_btn.pack(side=tk.RIGHT, padx=10)
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root,
            orient=tk.HORIZONTAL,
            mode='determinate'
        )
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 结果列表
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        ttk.Label(result_frame, text="操作结果:").pack(anchor=tk.W)
        
        self.result_text = tk.Text(
            result_frame,
            height=10,
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
    
    def browse_directory(self):
        """打开目录选择对话框"""
        selected_dir = filedialog.askdirectory()
        if selected_dir:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, selected_dir)
    
    def clean_files(self):
        """清理.bc!文件"""
        target_dir = self.dir_entry.get()
        recursive = self.recursive_var.get()
        
        if not target_dir:
            messagebox.showwarning("警告", "请先选择要清理的目录！")
            return
        
        if not os.path.isdir(target_dir):
            messagebox.showerror("错误", "指定的目录不存在或不是有效目录！")
            return
        
        self.log_message("开始扫描文件...")
        self.progress["value"] = 0
        self.root.update_idletasks()
        
        deleted_files = []
        error_files = []
        
        try:
            if recursive:
                # 递归搜索所有子目录
                for root_dir, _, files in os.walk(target_dir):
                    for filename in files:
                        if filename.endswith('.bc!'):
                            file_path = os.path.join(root_dir, filename)
                            try:
                                os.remove(file_path)
                                deleted_files.append(file_path)
                                self.log_message(f"已删除: {file_path}")
                            except Exception as e:
                                error_files.append(file_path)
                                self.log_message(f"删除失败: {file_path} - {str(e)}")
            else:
                # 仅搜索当前目录
                for filename in os.listdir(target_dir):
                    if filename.endswith('.bc!'):
                        file_path = os.path.join(target_dir, filename)
                        try:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            self.log_message(f"已删除: {file_path}")
                        except Exception as e:
                            error_files.append(file_path)
                            self.log_message(f"删除失败: {file_path} - {str(e)}")
            
            self.progress["value"] = 100
            self.status_var.set("清理完成")
            
            summary = (
                f"操作完成！\n"
                f"成功删除文件: {len(deleted_files)} 个\n"
                f"删除失败文件: {len(error_files)} 个"
            )
            
            self.log_message("\n" + summary)
            messagebox.showinfo("完成", summary)
            
        except Exception as e:
            self.log_message(f"清理过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"清理过程中发生错误: {str(e)}")
            self.status_var.set("清理失败")
    
    def log_message(self, message):
        """在结果区域显示消息"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)
        self.status_var.set(message)
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = BCFileCleanerApp(root)
    root.mainloop()