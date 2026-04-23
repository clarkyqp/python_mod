import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

class PDFToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF工具 - 拆分与合并")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建标签页
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 拆分标签页
        self.split_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.split_frame, text="PDF拆分")
        
        # 合并标签页
        self.merge_frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.merge_frame, text="PDF合并")
        
        self.setup_split_tab()
        self.setup_merge_tab()
    
    def setup_split_tab(self):
        """设置拆分标签页"""
        # 变量
        self.split_input_path = tk.StringVar()
        self.split_output_path = tk.StringVar()
        self.pages_per_file = tk.StringVar(value="50")
        self.split_progress = tk.DoubleVar()
        
        # 配置网格
        self.split_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(self.split_frame, text="PDF拆分工具", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入文件选择
        ttk.Label(self.split_frame, text="输入PDF文件:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.split_frame, textvariable=self.split_input_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))
        ttk.Button(self.split_frame, text="浏览", command=self.browse_split_input).grid(row=1, column=2, pady=5)
        
        # 输出目录选择
        ttk.Label(self.split_frame, text="输出目录:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.split_frame, textvariable=self.split_output_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(0, 5))
        ttk.Button(self.split_frame, text="浏览", command=self.browse_split_output).grid(row=2, column=2, pady=5)
        
        # 页数设置
        ttk.Label(self.split_frame, text="每文件页数:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(self.split_frame, textvariable=self.pages_per_file, width=20).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(self.split_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="开始拆分", command=self.start_split).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_split).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        ttk.Label(self.split_frame, text="进度:").grid(row=5, column=0, sticky=tk.W, pady=(20, 5))
        progress_bar = ttk.Progressbar(self.split_frame, variable=self.split_progress, maximum=100)
        progress_bar.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 5))
        
        # 状态显示
        self.split_status = tk.Text(self.split_frame, height=8, width=70, state=tk.DISABLED)
        self.split_status.grid(row=6, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self.split_frame, orient=tk.VERTICAL, command=self.split_status.yview)
        scrollbar.grid(row=6, column=3, sticky=(tk.N, tk.S), pady=10)
        self.split_status.configure(yscrollcommand=scrollbar.set)
        
        self.split_frame.rowconfigure(6, weight=1)
    
    def setup_merge_tab(self):
        """设置合并标签页"""
        # 变量
        self.merge_files = []  # 存储要合并的文件列表
        self.merge_output_path = tk.StringVar()
        self.merge_progress = tk.DoubleVar()
        
        # 配置网格
        self.merge_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(self.merge_frame, text="PDF合并工具", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件列表框架
        list_frame = ttk.LabelFrame(self.merge_frame, text="要合并的PDF文件", padding="10")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        
        # 文件列表和滚动条
        self.merge_listbox = tk.Listbox(list_frame, height=8)
        self.merge_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.merge_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky=(tk.N, tk.S))
        self.merge_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # 文件操作按钮
        file_button_frame = ttk.Frame(list_frame)
        file_button_frame.grid(row=1, column=0, columnspan=3, pady=5)
        
        ttk.Button(file_button_frame, text="添加文件", command=self.add_merge_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="添加文件夹", command=self.add_merge_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="上移", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="下移", command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="删除", command=self.remove_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_button_frame, text="清空列表", command=self.clear_merge_list).pack(side=tk.LEFT, padx=2)
        
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        
        # 输出文件
        ttk.Label(self.merge_frame, text="输出文件:").grid(row=2, column=0, sticky=tk.W, pady=10)
        ttk.Entry(self.merge_frame, textvariable=self.merge_output_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=10, padx=(0, 5))
        ttk.Button(self.merge_frame, text="浏览", command=self.browse_merge_output).grid(row=2, column=2, pady=10)
        
        # 按钮
        merge_button_frame = ttk.Frame(self.merge_frame)
        merge_button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(merge_button_frame, text="开始合并", command=self.start_merge).pack(side=tk.LEFT, padx=5)
        ttk.Button(merge_button_frame, text="清空", command=self.clear_merge).pack(side=tk.LEFT, padx=5)
        
        # 进度条
        ttk.Label(self.merge_frame, text="进度:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        progress_bar = ttk.Progressbar(self.merge_frame, variable=self.merge_progress, maximum=100)
        progress_bar.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # 状态显示
        self.merge_status = tk.Text(self.merge_frame, height=6, width=70, state=tk.DISABLED)
        self.merge_status.grid(row=5, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 滚动条
        merge_scrollbar = ttk.Scrollbar(self.merge_frame, orient=tk.VERTICAL, command=self.merge_status.yview)
        merge_scrollbar.grid(row=5, column=3, sticky=(tk.N, tk.S), pady=10)
        self.merge_status.configure(yscrollcommand=merge_scrollbar.set)
        
        self.merge_frame.rowconfigure(1, weight=1)
        self.merge_frame.rowconfigure(5, weight=1)
    
    # 拆分相关方法
    def browse_split_input(self):
        filename = filedialog.askopenfilename(
            title="选择要拆分的PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if filename:
            self.split_input_path.set(filename)
            if not self.split_output_path.get():
                self.split_output_path.set(os.path.dirname(filename))
    
    def browse_split_output(self):
        folder = filedialog.askdirectory(title="选择拆分输出目录")
        if folder:
            self.split_output_path.set(folder)
    
    def clear_split(self):
        self.split_input_path.set("")
        self.split_output_path.set("")
        self.pages_per_file.set("50")
        self.split_progress.set(0)
        self.update_split_status("", clear=True)
    
    def update_split_status(self, message, clear=False):
        self.split_status.config(state=tk.NORMAL)
        if clear:
            self.split_status.delete(1.0, tk.END)
        if message:
            self.split_status.insert(tk.END, message + "\n")
            self.split_status.see(tk.END)
        self.split_status.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def split_pdf(self):
        """执行PDF拆分"""
        input_path = self.split_input_path.get()
        output_path = self.split_output_path.get()
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入PDF文件")
            return False
        
        if not output_path:
            messagebox.showerror("错误", "请选择输出目录")
            return False
        
        try:
            pages_per_file = int(self.pages_per_file.get())
            if pages_per_file <= 0:
                messagebox.showerror("错误", "每文件页数必须大于0")
                return False
        except ValueError:
            messagebox.showerror("错误", "每文件页数必须是数字")
            return False
        
        if not os.path.exists(input_path):
            messagebox.showerror("错误", f"输入文件不存在: {input_path}")
            return False
        
        os.makedirs(output_path, exist_ok=True)
        
        try:
            self.update_split_status("正在读取PDF文件...")
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            
            self.update_split_status(f"PDF文件总页数: {total_pages}")
            self.update_split_status(f"每 {pages_per_file} 页拆分为一个文件")
            
            num_files = (total_pages + pages_per_file - 1) // pages_per_file
            self.update_split_status(f"将拆分为 {num_files} 个文件")
            
            input_filename = os.path.splitext(os.path.basename(input_path))[0]
            
            for file_index in range(num_files):
                writer = PdfWriter()
                
                start_page = file_index * pages_per_file
                end_page = min((file_index + 1) * pages_per_file, total_pages)
                
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                output_filename = f"{input_filename}_part{file_index + 1:03d}.pdf"
                output_file_path = os.path.join(output_path, output_filename)
                
                with open(output_file_path, 'wb') as output_file:
                    writer.write(output_file)
                
                progress_value = (file_index + 1) / num_files * 100
                self.split_progress.set(progress_value)
                
                status_msg = f"已创建: {output_filename} (页 {start_page + 1}-{end_page})"
                self.update_split_status(status_msg)
            
            self.update_split_status(f"\n拆分完成！共生成 {num_files} 个文件")
            self.split_progress.set(100)
            
            messagebox.showinfo("完成", f"PDF拆分完成！\n共生成 {num_files} 个文件")
            return True
            
        except Exception as e:
            error_msg = f"处理PDF文件时出错: {str(e)}"
            self.update_split_status(error_msg)
            messagebox.showerror("错误", error_msg)
            return False
    
    def start_split(self):
        import threading
        thread = threading.Thread(target=self.split_pdf)
        thread.daemon = True
        thread.start()
    
    # 合并相关方法
    def add_merge_files(self):
        files = filedialog.askopenfilenames(
            title="选择要合并的PDF文件",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        for file in files:
            if file not in self.merge_files:
                self.merge_files.append(file)
                self.merge_listbox.insert(tk.END, os.path.basename(file))
        
        if files and not self.merge_output_path.get():
            dir_name = os.path.dirname(files[0])
            self.merge_output_path.set(os.path.join(dir_name, "merged.pdf"))
    
    def add_merge_folder(self):
        folder = filedialog.askdirectory(title="选择包含PDF文件的文件夹")
        if folder:
            pdf_files = []
            for file in os.listdir(folder):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(folder, file))
            
            # 按文件名排序
            pdf_files.sort()
            
            for file in pdf_files:
                if file not in self.merge_files:
                    self.merge_files.append(file)
                    self.merge_listbox.insert(tk.END, os.path.basename(file))
            
            if pdf_files and not self.merge_output_path.get():
                self.merge_output_path.set(os.path.join(folder, "merged.pdf"))
    
    def move_up(self):
        selected = self.merge_listbox.curselection()
        if selected and selected[0] > 0:
            index = selected[0]
            # 交换列表中的元素
            self.merge_files[index], self.merge_files[index-1] = self.merge_files[index-1], self.merge_files[index]
            # 更新列表框
            self.refresh_merge_list()
            self.merge_listbox.select_set(index-1)
    
    def move_down(self):
        selected = self.merge_listbox.curselection()
        if selected and selected[0] < len(self.merge_files) - 1:
            index = selected[0]
            # 交换列表中的元素
            self.merge_files[index], self.merge_files[index+1] = self.merge_files[index+1], self.merge_files[index]
            # 更新列表框
            self.refresh_merge_list()
            self.merge_listbox.select_set(index+1)
    
    def remove_file(self):
        selected = self.merge_listbox.curselection()
        if selected:
            index = selected[0]
            self.merge_files.pop(index)
            self.refresh_merge_list()
    
    def clear_merge_list(self):
        self.merge_files.clear()
        self.merge_listbox.delete(0, tk.END)
    
    def refresh_merge_list(self):
        self.merge_listbox.delete(0, tk.END)
        for file in self.merge_files:
            self.merge_listbox.insert(tk.END, os.path.basename(file))
    
    def browse_merge_output(self):
        filename = filedialog.asksaveasfilename(
            title="选择合并输出文件",
            defaultextension=".pdf",
            filetypes=[("PDF文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if filename:
            self.merge_output_path.set(filename)
    
    def clear_merge(self):
        self.clear_merge_list()
        self.merge_output_path.set("")
        self.merge_progress.set(0)
        self.update_merge_status("", clear=True)
    
    def update_merge_status(self, message, clear=False):
        self.merge_status.config(state=tk.NORMAL)
        if clear:
            self.merge_status.delete(1.0, tk.END)
        if message:
            self.merge_status.insert(tk.END, message + "\n")
            self.merge_status.see(tk.END)
        self.merge_status.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def merge_pdfs(self):
        """执行PDF合并"""
        if not self.merge_files:
            messagebox.showerror("错误", "请添加要合并的PDF文件")
            return False
        
        output_path = self.merge_output_path.get()
        if not output_path:
            messagebox.showerror("错误", "请选择输出文件路径")
            return False
        
        try:
            self.update_merge_status("开始合并PDF文件...")
            merger = PdfMerger()
            
            total_files = len(self.merge_files)
            
            for i, file_path in enumerate(self.merge_files):
                try:
                    self.update_merge_status(f"正在处理: {os.path.basename(file_path)}")
                    merger.append(file_path)
                    
                    # 更新进度
                    progress_value = (i + 1) / total_files * 100
                    self.merge_progress.set(progress_value)
                    
                except Exception as e:
                    self.update_merge_status(f"错误: 无法处理文件 {os.path.basename(file_path)} - {str(e)}")
                    continue
            
            self.update_merge_status("正在保存合并后的文件...")
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            
            self.update_merge_status(f"\n合并完成！输出文件: {output_path}")
            self.merge_progress.set(100)
            
            messagebox.showinfo("完成", f"PDF合并完成！\n输出文件: {os.path.basename(output_path)}")
            return True
            
        except Exception as e:
            error_msg = f"合并PDF文件时出错: {str(e)}"
            self.update_merge_status(error_msg)
            messagebox.showerror("错误", error_msg)
            return False
    
    def start_merge(self):
        import threading
        thread = threading.Thread(target=self.merge_pdfs)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = PDFToolsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()