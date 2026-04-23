import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class VideoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频文件整理工具")
        self.root.geometry("700x500")
        
        # 默认视频扩展名
        self.video_extensions = [
            '.mp4', '.avi', '.mov', '.mkv', '.flv', 
            '.wmv', '.webm', '.mpeg', '.mpg', '.3gp',
            '.m4v', '.ts', '.rm', '.rmvb', '.vob',
            '.gif'
        ]
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # 文件夹选择部分
        folder_frame = tk.LabelFrame(main_frame, text="选择源文件夹", padx=10, pady=10)
        folder_frame.pack(fill="x")
        
        self.folder_path = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side="left", padx=5)
        tk.Button(folder_frame, text="浏览...", command=self.select_folder).pack(side="left")
        
        # 扩展名设置部分
        ext_frame = tk.LabelFrame(main_frame, text="视频文件扩展名（用逗号分隔）", padx=10, pady=10)
        ext_frame.pack(fill="both", expand=True, pady=10)
        
        self.ext_text = ScrolledText(ext_frame, height=5)
        self.ext_text.insert("1.0", ", ".join(self.video_extensions))
        self.ext_text.pack(fill="both", expand=True)
        
        # 选项部分
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill="x", pady=5)
        
        self.keep_structure = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="保持子文件夹结构", variable=self.keep_structure).pack(side="left")
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)
        
        # 操作按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="开始整理", command=self.start_organizing, width=15).pack(side="left", padx=5)
        tk.Button(btn_frame, text="清空日志", command=self.clear_log, width=15).pack(side="left", padx=5)
        
        # 日志输出
        log_frame = tk.LabelFrame(self.root, text="操作日志", padx=10, pady=10)
        log_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log_text = ScrolledText(log_frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="选择源文件夹")
        if folder:
            self.folder_path.set(folder)
    
    def update_extensions(self):
        ext_text = self.ext_text.get("1.0", "end-1c")
        self.video_extensions = [ext.strip().lower() for ext in ext_text.split(",") if ext.strip()]
    
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def start_organizing(self):
        source_folder = self.folder_path.get()
        if not source_folder or not os.path.isdir(source_folder):
            messagebox.showerror("错误", "请选择有效的源文件夹！")
            return
        
        self.update_extensions()
        keep_structure = self.keep_structure.get()
        
        # 创建视频文件夹
        video_folder = os.path.join(source_folder, "视频")
        os.makedirs(video_folder, exist_ok=True)
        
        # 查找所有视频文件
        video_files = []
        for root, _, files in os.walk(source_folder):
            # 跳过视频文件夹本身
            if os.path.abspath(root) == os.path.abspath(video_folder):
                continue
                
            for file in files:
                if os.path.splitext(file)[1].lower() in self.video_extensions:
                    video_files.append((root, file))
        
        total_files = len(video_files)
        if total_files == 0:
            self.log_message("没有找到视频文件！")
            return
        
        self.progress["maximum"] = total_files
        self.progress["value"] = 0
        
        moved_count = 0
        errors = []
        
        for i, (root, file) in enumerate(video_files, 1):
            src_path = os.path.join(root, file)
            
            if keep_structure:
                # 保持子文件夹结构
                rel_path = os.path.relpath(root, source_folder)
                dest_dir = os.path.join(video_folder, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, file)
            else:
                # 不保持结构，直接放在视频文件夹
                dest_path = os.path.join(video_folder, file)
                # 处理文件名冲突
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(file)
                    dest_path = os.path.join(video_folder, f"{name}_{counter}{ext}")
                    counter += 1
            
            try:
                shutil.move(src_path, dest_path)
                moved_count += 1
                self.log_message(f"已移动: {file}")
            except Exception as e:
                errors.append(f"移动失败 {file}: {str(e)}")
                self.log_message(f"[错误] {errors[-1]}")
            
            self.progress["value"] = i
            self.root.update_idletasks()
        
        # 显示结果
        result_msg = (
            f"\n===== 整理完成 =====\n"
            f"找到视频文件: {total_files}\n"
            f"成功移动: {moved_count}\n"
            f"失败: {len(errors)}"
        )
        
        if errors:
            result_msg += "\n\n错误示例:\n" + "\n".join(errors[:3])
            if len(errors) > 3:
                result_msg += f"\n(还有 {len(errors)-3} 个错误未显示...)"
        
        self.log_message(result_msg)
        messagebox.showinfo("完成", f"整理完成！\n共找到 {total_files} 个视频文件\n成功移动 {moved_count} 个")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoOrganizerApp(root)
    root.mainloop()