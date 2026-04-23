import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class FileRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件重命名工具")
        self.root.geometry("700x500")
        
        self.setup_ui()
    
    def setup_ui(self):
        # 选择文件夹部分
        folder_frame = tk.LabelFrame(self.root, text="选择包含子文件夹的目录", padx=10, pady=10)
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        self.folder_path = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side="left", padx=5)
        tk.Button(folder_frame, text="浏览...", command=self.browse_folder).pack(side="left")
        
        # 命名格式设置
        format_frame = tk.LabelFrame(self.root, text="命名格式设置", padx=10, pady=10)
        format_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Label(format_frame, text="文件名格式:").pack(side="left")
        self.name_format = tk.StringVar(value="{parent}_{index}{ext}")
        tk.Entry(format_frame, textvariable=self.name_format, width=30).pack(side="left", padx=5)
        
        tk.Label(format_frame, text="起始序号:").pack(side="left", padx=(10,0))
        self.start_index = tk.IntVar(value=1)
        tk.Spinbox(format_frame, from_=1, to=999, textvariable=self.start_index, width=5).pack(side="left")
        
        # 选项设置
        option_frame = tk.Frame(self.root)
        option_frame.pack(pady=5, fill="x")
        
        self.skip_existing = tk.BooleanVar(value=True)
        tk.Checkbutton(option_frame, text="跳过已存在文件", variable=self.skip_existing).pack(side="left", padx=10)
        
        self.sort_files = tk.BooleanVar(value=True)
        tk.Checkbutton(option_frame, text="按名称排序文件", variable=self.sort_files).pack(side="left", padx=10)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=10)
        
        # 操作按钮
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="预览重命名", command=self.preview_rename, width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="执行重命名", command=self.execute_rename, width=15).pack(side="left", padx=10)
        
        # 日志输出
        self.log_text = ScrolledText(self.root, height=15, state="disabled")
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.log_message(f"已选择目录: {folder_selected}")
    
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
    
    def get_files_to_rename(self):
        current_dir = Path(self.folder_path.get())
        if not current_dir.exists():
            messagebox.showerror("错误", "请选择有效的目录！")
            return None
        
        subdirs = [d for d in current_dir.iterdir() if d.is_dir()]
        if not subdirs:
            messagebox.showwarning("警告", "所选目录中没有子文件夹！")
            return None
        
        all_files = {}
        for subdir in subdirs:
            files = [f for f in subdir.iterdir() if f.is_file()]
            if self.sort_files.get():
                files.sort()
            all_files[subdir] = files
        
        return all_files
    
    def preview_rename(self):
        self.clear_log()
        all_files = self.get_files_to_rename()
        if not all_files:
            return
        
        self.log_message("=== 预览重命名结果 ===")
        total_files = 0
        
        for subdir, files in all_files.items():
            self.log_message(f"\n文件夹: {subdir.name}")
            
            for index, file in enumerate(files, start=self.start_index.get()):
                new_name = self.name_format.get().format(
                    parent=subdir.name,
                    index=index,
                    ext=file.suffix
                )
                new_path = subdir / new_name
                
                if new_path.exists() and self.skip_existing.get():
                    self.log_message(f" [跳过] {file.name} -> {new_name} (文件已存在)")
                else:
                    self.log_message(f" [重命名] {file.name} -> {new_name}")
                
                total_files += 1
        
        self.log_message(f"\n总计: {len(all_files)} 个子文件夹, {total_files} 个文件将被处理")
    
    def execute_rename(self):
        self.clear_log()
        all_files = self.get_files_to_rename()
        if not all_files:
            return
        
        total_subdirs = len(all_files)
        total_files = sum(len(files) for files in all_files.values())
        processed_files = 0
        skipped_files = 0
        renamed_files = 0
        errors = []
        
        self.progress["maximum"] = total_files
        self.progress["value"] = 0
        
        self.log_message("=== 开始执行重命名 ===")
        
        for subdir, files in all_files.items():
            self.log_message(f"\n处理文件夹: {subdir.name}")
            
            for index, file in enumerate(files, start=self.start_index.get()):
                try:
                    new_name = self.name_format.get().format(
                        parent=subdir.name,
                        index=index,
                        ext=file.suffix
                    )
                    new_path = subdir / new_name
                    
                    if new_path.exists() and self.skip_existing.get():
                        self.log_message(f" [跳过] {file.name} -> {new_name}")
                        skipped_files += 1
                    else:
                        file.rename(new_path)
                        self.log_message(f" [已重命名] {file.name} -> {new_name}")
                        renamed_files += 1
                    
                    processed_files += 1
                    self.progress["value"] = processed_files
                    self.root.update_idletasks()
                
                except Exception as e:
                    error_msg = f"重命名 {file.name} 失败: {str(e)}"
                    errors.append(error_msg)
                    self.log_message(f" [错误] {error_msg}")
                    processed_files += 1
                    self.progress["value"] = processed_files
        
        # 显示结果
        result_msg = (
            f"\n=== 重命名完成 ===\n"
            f"子文件夹数: {total_subdirs}\n"
            f"总文件数: {total_files}\n"
            f"成功重命名: {renamed_files}\n"
            f"跳过: {skipped_files}\n"
            f"错误: {len(errors)}"
        )
        
        if errors:
            result_msg += "\n\n错误示例:\n" + "\n".join(errors[:3])
            if len(errors) > 3:
                result_msg += f"\n(还有 {len(errors)-3} 个错误未显示...)"
        
        self.log_message(result_msg)
        messagebox.showinfo("完成", f"重命名操作完成！\n成功: {renamed_files}, 跳过: {skipped_files}, 错误: {len(errors)}")
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = FileRenamerApp(root)
    root.mainloop()