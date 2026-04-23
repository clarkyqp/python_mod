import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class BatchFileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件移动工具")
        self.root.geometry("500x300")
        
        # 变量
        self.folder_path = tk.StringVar()
        self.batch_size = tk.IntVar(value=100)
        self.status = tk.StringVar(value="准备就绪")
        
        # 创建UI元素
        self.create_widgets()
    
    def create_widgets(self):
        # 文件夹选择部分
        frame_folder = ttk.LabelFrame(self.root, text="选择文件夹")
        frame_folder.pack(pady=10, padx=10, fill="x")
        
        ttk.Entry(frame_folder, textvariable=self.folder_path, width=50).pack(side="left", padx=5)
        ttk.Button(frame_folder, text="浏览...", command=self.browse_folder).pack(side="left", padx=5)
        
        # 批量大小设置
        frame_batch = ttk.LabelFrame(self.root, text="设置每批文件数量")
        frame_batch.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(frame_batch, text="每批文件数:").pack(side="left", padx=5)
        ttk.Entry(frame_batch, textvariable=self.batch_size, width=10).pack(side="left", padx=5)
        
        # 操作按钮
        frame_buttons = ttk.Frame(self.root)
        frame_buttons.pack(pady=10)
        
        ttk.Button(frame_buttons, text="开始移动文件", command=self.move_files).pack(side="left", padx=10)
        ttk.Button(frame_buttons, text="退出", command=self.root.quit).pack(side="left", padx=10)
        
        # 状态栏
        ttk.Label(self.root, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", padx=10, pady=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.status.set(f"已选择文件夹: {folder_selected}")
    
    def move_files(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("错误", "请先选择文件夹！")
            return
        
        batch_size = self.batch_size.get()
        if batch_size <= 0:
            messagebox.showerror("错误", "每批文件数必须大于0！")
            return
        
        try:
            # 获取当前目录下所有文件（排除目录）
            files = [f for f in os.listdir(folder) 
                    if os.path.isfile(os.path.join(folder, f))]
            
            if not files:
                messagebox.showinfo("信息", "所选文件夹中没有文件可移动！")
                return
            
            # 按文件名排序
            files.sort()
            
            # 计算需要创建多少个子文件夹
            num_batches = (len(files) + batch_size - 1) // batch_size
            
            self.progress["maximum"] = len(files)
            moved_files = 0
            
            for i in range(1, num_batches + 1):
                # 创建子文件夹
                subfolder = os.path.join(folder, str(i))
                os.makedirs(subfolder, exist_ok=True)
                
                # 计算这一批的文件范围
                start = (i - 1) * batch_size
                end = i * batch_size
                batch_files = files[start:end]
                
                # 移动文件
                for file in batch_files:
                    src = os.path.join(folder, file)
                    dst = os.path.join(subfolder, file)
                    shutil.move(src, dst)
                    moved_files += 1
                    self.progress["value"] = moved_files
                    self.status.set(f"正在移动文件: {file} 到 {subfolder}")
                    self.root.update_idletasks()
            
            messagebox.showinfo("完成", f"文件移动完成！共移动了 {len(files)} 个文件到 {num_batches} 个子文件夹中。")
            self.status.set("文件移动完成")
            self.progress["value"] = 0
            
        except Exception as e:
            messagebox.showerror("错误", f"发生错误: {str(e)}")
            self.status.set("操作失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchFileMoverApp(root)
    root.mainloop()