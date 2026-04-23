import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

class VideoSizeAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("视频文件大小分析工具")
        self.root.geometry("1000x700")
        
        # 视频扩展名列表
        self.video_extensions = [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv',
            '.webm', '.mpeg', '.mpg', '.3gp', '.m4v', '.ogg',
            '.ts', '.m2ts', '.rmvb', '.asf', '.divx'
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # 顶部控制面板
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)
        
        # 文件夹选择按钮
        self.folder_path = tk.StringVar()
        tk.Label(control_frame, text="选择文件夹:").pack(side=tk.LEFT)
        tk.Entry(control_frame, textvariable=self.folder_path, width=70).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="浏览...", command=self.select_folder).pack(side=tk.LEFT)
        
        # 分析按钮
        tk.Button(control_frame, text="开始分析", command=self.analyze_folder).pack(side=tk.LEFT, padx=10)
        
        # 结果显示区域
        result_frame = tk.Frame(self.root)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 树状表格
        self.tree = ttk.Treeview(result_frame, columns=('size'), show='tree headings')
        self.tree.heading('#0', text='文件/文件夹名称')
        self.tree.heading('size', text='大小')
        self.tree.column('#0', width=700, anchor='w')
        self.tree.column('size', width=150, anchor='e')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 底部统计信息
        self.total_label = tk.Label(self.root, text="请选择文件夹并点击'开始分析'", font=('Arial', 10))
        self.total_label.pack(pady=10)
        
        # 右键菜单
        self.setup_context_menu()
    
    def setup_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="复制路径", command=self.copy_path)
        self.menu.add_command(label="打开所在文件夹", command=self.open_folder)
        
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)
    
    def copy_path(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            path = item['text'] if 'fullpath' not in item['values'] else item['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            messagebox.showinfo("复制成功", f"已复制路径:\n{path}")
    
    def open_folder(self):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            path = item['text'] if 'fullpath' not in item['values'] else os.path.dirname(item['values'][0])
            try:
                os.startfile(path)
            except:
                messagebox.showerror("错误", f"无法打开文件夹:\n{path}")
    
    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
    
    def analyze_folder(self):
        directory = self.folder_path.get()
        if not directory:
            messagebox.showwarning("警告", "请先选择文件夹")
            return
        
        # 清空之前的统计结果
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 显示进度
        self.total_label.config(text="正在分析，请稍候...")
        self.root.update()
        
        try:
            # 开始分析
            total_size, total_count = self.process_directory(directory)
            
            # 更新总计信息
            self.total_label.config(
                text=f"总计: {total_count} 个视频文件, 总大小: {self.format_size(total_size)}"
            )
        except Exception as e:
            messagebox.showerror("错误", f"分析过程中出错:\n{str(e)}")
            self.total_label.config(text="分析失败")
    
    def process_directory(self, directory):
        total_size = 0
        total_count = 0
        
        # 先添加根文件夹节点
        root_node = self.tree.insert('', 'end', text=directory, values=('',))
        
        for root, dirs, files in os.walk(directory):
            # 获取相对于根目录的路径
            rel_path = os.path.relpath(root, directory)
            if rel_path == '.':
                parent_node = root_node
            else:
                # 查找或创建父节点
                path_parts = rel_path.split(os.sep)
                parent_node = root_node
                for part in path_parts:
                    found = False
                    for child in self.tree.get_children(parent_node):
                        if self.tree.item(child)['text'] == part:
                            parent_node = child
                            found = True
                            break
                    if not found:
                        parent_node = self.tree.insert(parent_node, 'end', text=part, values=('',))
            
            # 处理当前目录中的视频文件
            dir_size = 0
            dir_count = 0
            for file in files:
                if any(file.lower().endswith(ext) for ext in self.video_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        self.tree.insert(parent_node, 'end', 
                                          text=file, 
                                          values=(self.format_size(file_size), file_path))
                        dir_size += file_size
                        dir_count += 1
                    except OSError as e:
                        print(f"无法获取文件大小 {file_path}: {e}")
            
            # 更新文件夹节点的总大小
            if dir_count > 0:
                self.tree.item(parent_node, values=(self.format_size(dir_size),))
                total_size += dir_size
                total_count += dir_count
        
        return total_size, total_count
    
    def format_size(self, size_bytes):
        # 将字节转换为更友好的单位
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoSizeAnalyzer(root)
    root.mainloop()