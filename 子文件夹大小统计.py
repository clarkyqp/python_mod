import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from threading import Thread

class FolderSizeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("文件夹大小计算器(GB)")
        self.root.geometry("700x500")
        
        # 当前选择的目录
        self.current_dir = os.getcwd()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建所有UI组件"""
        # 顶部框架 - 目录选择和计算按钮
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, fill='x', padx=10)
        
        # 目录选择按钮
        dir_btn = tk.Button(top_frame, text="选择目录", command=self.select_directory)
        dir_btn.pack(side='left', padx=5)
        
        # 当前路径显示
        self.dir_label = tk.Label(top_frame, text=f"当前目录: {self.current_dir}", anchor='w')
        self.dir_label.pack(side='left', fill='x', expand=True, padx=5)
        
        # 计算按钮
        calculate_btn = tk.Button(top_frame, text="计算子文件夹大小", command=self.start_calculation_thread)
        calculate_btn.pack(side='right', padx=5)
        
        # 进度标签
        self.progress_label = tk.Label(self.root, text="请先选择目录", anchor='w')
        self.progress_label.pack(fill='x', padx=10, pady=5)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', mode='determinate')
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        
        # 结果表格框架
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 结果表格
        columns = ("folder", "size")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading("folder", text="文件夹名称")
        self.tree.heading("size", text="大小(GB)")
        self.tree.column("folder", width=500)
        self.tree.column("size", width=150)
        
        # 滚动条
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')
        
        # 底部信息
        self.status_label = tk.Label(self.root, text="", anchor='w')
        self.status_label.pack(fill='x', padx=10, pady=5)
    
    def select_directory(self):
        """选择要分析的目录"""
        selected_dir = filedialog.askdirectory(title="选择目录", initialdir=self.current_dir)
        if selected_dir:
            self.current_dir = selected_dir
            self.dir_label.config(text=f"当前目录: {self.current_dir}")
            self.clear_results()
    
    def clear_results(self):
        """清除之前的计算结果"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.progress_bar['value'] = 0
        self.progress_label.config(text="已选择新目录，请点击计算按钮")
        self.status_label.config(text="")
    
    def get_folder_size(self, folder_path):
        """计算文件夹大小（单位：GB）"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    continue
        return total_size / (1024 * 1024 * 1024)  # 转换为GB
    
    def calculate_subfolders(self):
        """计算子文件夹大小"""
        try:
            subfolders = [f for f in os.listdir(self.current_dir) 
                         if os.path.isdir(os.path.join(self.current_dir, f))]
            
            if not subfolders:
                self.progress_label.config(text="所选目录中没有子文件夹")
                self.status_label.config(text="状态: 完成 - 没有子文件夹")
                return
            
            # 清空表格
            for row in self.tree.get_children():
                self.tree.delete(row)
            
            total_size = 0
            folder_count = len(subfolders)
            self.progress_bar['maximum'] = folder_count
            
            for i, folder in enumerate(subfolders, 1):
                folder_path = os.path.join(self.current_dir, folder)
                size_gb = self.get_folder_size(folder_path)
                total_size += size_gb
                # 根据大小自动选择合适的显示格式
                if size_gb >= 1:
                    size_str = f"{size_gb:.2f} GB"
                else:
                    size_str = f"{size_gb:.4f} GB"  # 小于1GB时显示更多小数位
                self.tree.insert('', 'end', values=(folder, size_str))
                self.progress_bar['value'] = i
                self.progress_label.config(text=f"处理中: {i}/{folder_count}")
                self.root.update_idletasks()
            
            self.progress_label.config(text="计算完成")
            # 格式化总大小显示
            if total_size >= 1:
                total_str = f"{total_size:.2f} GB"
            else:
                total_str = f"{total_size:.4f} GB"
            self.status_label.config(text=f"状态: 完成 - 共 {folder_count} 个子文件夹, 总大小: {total_str}")
        
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            self.progress_label.config(text="计算出错")
            self.status_label.config(text=f"状态: 错误 - {str(e)}")
    
    def start_calculation_thread(self):
        """在新线程中启动计算，避免UI冻结"""
        if not os.path.isdir(self.current_dir):
            messagebox.showwarning("警告", "请先选择有效目录")
            return
        
        self.progress_label.config(text="准备中...")
        self.progress_bar['value'] = 0
        self.status_label.config(text="状态: 计算中...")
        
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        thread = Thread(target=self.calculate_subfolders)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderSizeCalculator(root)
    root.mainloop()