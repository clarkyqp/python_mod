import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class FileClassifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件分类工具 (多文件夹版)")
        self.root.geometry("600x450")
        
        # 视频扩展名列表
        self.video_extensions = [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', 
            '.wmv', '.webm', '.mpeg', '.mpg', '.3gp',
            '.m4v', '.ts', '.rm', '.rmvb', '.vob'
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # 选择文件夹部分
        folder_frame = tk.LabelFrame(self.root, text="选择文件夹（可多选）", padx=10, pady=10)
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        self.folder_listbox = tk.Listbox(folder_frame, height=4, selectmode=tk.EXTENDED)
        self.folder_listbox.pack(side="left", fill="both", expand=True, padx=5)
        
        btn_frame = tk.Frame(folder_frame)
        btn_frame.pack(side="right", fill="y")
        
        tk.Button(btn_frame, text="添加文件夹", command=self.add_folders).pack(pady=5)
        tk.Button(btn_frame, text="移除选中", command=self.remove_selected).pack(pady=5)
        tk.Button(btn_frame, text="清空列表", command=self.clear_list).pack(pady=5)
        
        # 扩展名设置部分
        ext_frame = tk.LabelFrame(self.root, text="视频文件扩展名（用逗号分隔）", padx=10, pady=10)
        ext_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.ext_text = ScrolledText(ext_frame, height=5, width=60)
        self.ext_text.insert("1.0", ", ".join(self.video_extensions))
        self.ext_text.pack()
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate")
        self.progress.pack(pady=10)
        
        # 分类按钮
        tk.Button(self.root, text="开始分类所有文件夹", command=self.classify_all_folders, 
                 height=2, width=20).pack(pady=10)
        
        # 日志输出
        self.log_text = ScrolledText(self.root, height=8, state="disabled")
        self.log_text.pack(pady=5, padx=10, fill="both", expand=True)
    
    def add_folders(self):
        folder = filedialog.askdirectory(mustexist=True, title="选择要分类的文件夹")
        if folder and folder not in self.folder_listbox.get(0, tk.END):
            self.folder_listbox.insert(tk.END, folder)
    
    def remove_selected(self):
        for i in reversed(self.folder_listbox.curselection()):
            self.folder_listbox.delete(i)
    
    def clear_list(self):
        self.folder_listbox.delete(0, tk.END)
    
    def update_extensions(self):
        ext_text = self.ext_text.get("1.0", "end-1c")
        self.video_extensions = [ext.strip().lower() for ext in ext_text.split(",") if ext.strip()]
    
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
    
    def classify_files(self, source_folder):
        self.update_extensions()
        
        video_folder = os.path.join(source_folder, "视频")
        non_video_folder = os.path.join(source_folder, "非视频")
        
        os.makedirs(video_folder, exist_ok=True)
        os.makedirs(non_video_folder, exist_ok=True)
        
        files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
        total_files = len(files)
        
        if total_files == 0:
            self.log_message(f"[{os.path.basename(source_folder)}] 没有可分类的文件")
            return 0, 0, []
        
        moved_files = 0
        errors = []
        
        for filename in files:
            file_path = os.path.join(source_folder, filename)
            
            try:
                _, ext = os.path.splitext(filename)
                ext = ext.lower()
                
                if ext in self.video_extensions:
                    dest = os.path.join(video_folder, filename)
                    self.log_message(f"[视频] {filename}")
                else:
                    dest = os.path.join(non_video_folder, filename)
                    self.log_message(f"[其他] {filename}")
                
                shutil.move(file_path, dest)
                moved_files += 1
            except Exception as e:
                error_msg = f"移动文件 {filename} 失败: {str(e)}"
                errors.append(error_msg)
                self.log_message(f"[错误] {error_msg}")
        
        return total_files, moved_files, errors
    
    def classify_all_folders(self):
        folders = self.folder_listbox.get(0, tk.END)
        if not folders:
            messagebox.showerror("错误", "请先添加要分类的文件夹！")
            return
        
        total_folders = len(folders)
        self.progress["maximum"] = total_folders
        self.progress["value"] = 0
        
        total_files_all = 0
        moved_files_all = 0
        errors_all = []
        
        for i, folder in enumerate(folders, 1):
            self.log_message(f"\n=== 正在处理文件夹: {folder} ===")
            total_files, moved_files, errors = self.classify_files(folder)
            
            total_files_all += total_files
            moved_files_all += moved_files
            errors_all.extend(errors)
            
            self.progress["value"] = i
            self.root.update_idletasks()
        
        # 显示最终结果
        result_msg = (
            f"\n===== 分类完成 =====\n"
            f"总文件夹数: {total_folders}\n"
            f"总文件数: {total_files_all}\n"
            f"成功移动: {moved_files_all}\n"
            f"失败: {len(errors_all)}"
        )
        
        if errors_all:
            result_msg += "\n\n错误示例:\n" + "\n".join(errors_all[:3])
            if len(errors_all) > 3:
                result_msg += f"\n(还有 {len(errors_all)-3} 个错误未显示...)"
        
        self.log_message(result_msg)
        messagebox.showinfo("完成", f"已处理 {total_folders} 个文件夹\n移动 {moved_files_all}/{total_files_all} 个文件")
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = FileClassifierApp(root)
    root.mainloop()