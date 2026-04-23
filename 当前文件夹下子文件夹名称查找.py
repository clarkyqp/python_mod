import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class DirectSubfolderFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("直接子文件夹查找工具")
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 窗口大小和位置
        self.root.geometry("500x400")
        self.center_window()
        
        # 主界面布局
        self.create_directory_selector()
        self.create_search_controls()
        self.create_results_display()
        
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_directory_selector(self):
        """创建目录选择部分"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.X)
        
        ttk.Label(frame, text="目标目录:").pack(side=tk.LEFT)
        
        self.dir_path = tk.StringVar(value=os.getcwd())
        ttk.Entry(frame, textvariable=self.dir_path, width=40).pack(
            side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        ttk.Button(frame, text="浏览...", command=self.select_directory).pack(side=tk.LEFT)
        
    def create_search_controls(self):
        """创建搜索控制部分"""
        frame = ttk.Frame(self.root, padding="10")
        frame.pack(fill=tk.X)
        
        # 搜索输入框
        ttk.Label(frame, text="搜索名称:").pack(side=tk.LEFT)
        self.search_term = ttk.Entry(frame, width=30)
        self.search_term.pack(side=tk.LEFT, padx=5)
        
        # 搜索选项
        self.case_sensitive = tk.BooleanVar()
        ttk.Checkbutton(frame, text="区分大小写", variable=self.case_sensitive).pack(side=tk.LEFT, padx=5)
        
        # 搜索按钮
        ttk.Button(frame, text="搜索子文件夹", command=self.perform_search).pack(side=tk.RIGHT)
        
    def create_results_display(self):
        """创建结果显示部分"""
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 结果树状图
        self.results_tree = ttk.Treeview(frame, columns=("path"), show="headings")
        self.results_tree.heading("path", text="匹配的子文件夹路径")
        self.results_tree.column("path", width=450)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscroll=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右键菜单
        self.setup_context_menu()
        
    def setup_context_menu(self):
        """设置右键上下文菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="打开文件夹", command=self.open_folder)
        self.context_menu.add_command(label="复制路径", command=self.copy_path)
        self.results_tree.bind("<Button-3>", self.show_context_menu)
        
    def select_directory(self):
        """选择目标目录"""
        directory = filedialog.askdirectory(initialdir=self.dir_path.get())
        if directory:
            self.dir_path.set(directory)
            
    def perform_search(self):
        """执行搜索操作"""
        # 清除旧结果
        self.results_tree.delete(*self.results_tree.get_children())
        
        # 获取输入参数
        target_dir = self.dir_path.get()
        search_text = self.search_term.get().strip()
        
        # 验证输入
        if not search_text:
            messagebox.showwarning("输入错误", "请输入要搜索的文件夹名称")
            return
            
        if not os.path.isdir(target_dir):
            messagebox.showerror("目录错误", "指定的目录不存在或不可访问")
            return
            
        # 执行搜索
        matches = self.find_subfolders(target_dir, search_text)
        
        # 显示结果
        if matches:
            for path in matches:
                self.results_tree.insert("", tk.END, values=(path,))
        else:
            messagebox.showinfo("搜索结果", f"在 {target_dir} 的直接子文件夹中未找到匹配项")
            
    def find_subfolders(self, directory, search_term):
        """查找匹配的子文件夹"""
        matches = []
        case_sensitive = self.case_sensitive.get()
        
        try:
            for item in os.listdir(directory):
                full_path = os.path.join(directory, item)
                if os.path.isdir(full_path):
                    if case_sensitive:
                        if search_term in item:
                            matches.append(full_path)
                    else:
                        if search_term.lower() in item.lower():
                            matches.append(full_path)
        except PermissionError:
            messagebox.showerror("权限错误", "没有权限访问该目录的内容")
            
        return matches
        
    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)
            
    def open_folder(self):
        """打开选中的文件夹"""
        selected = self.results_tree.selection()
        if selected:
            path = self.results_tree.item(selected[0])["values"][0]
            self.open_file_explorer(path)
            
    def copy_path(self):
        """复制路径到剪贴板"""
        selected = self.results_tree.selection()
        if selected:
            path = self.results_tree.item(selected[0])["values"][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(path)
            messagebox.showinfo("成功", "路径已复制到剪贴板")
            
    @staticmethod
    def open_file_explorer(path):
        """使用系统文件管理器打开路径"""
        try:
            if os.name == "nt":  # Windows
                os.startfile(path)
            elif os.name == "posix":  # macOS/Linux
                os.system(f'open "{path}"' if sys.platform == "darwin" else f'xdg-open "{path}"')
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")

if __name__ == "__main__":
    import sys
    root = tk.Tk()
    app = DirectSubfolderFinder(root)
    root.mainloop()