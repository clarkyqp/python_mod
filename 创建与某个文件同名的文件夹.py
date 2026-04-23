import os
import tkinter as tk
from tkinter import filedialog, messagebox

def create_folder_from_file():
    # 创建主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("所有文件", "*.*")]
    )

    if not file_path:
        return  # 用户取消了选择

    # 获取文件名和目录
    file_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    file_base_name = os.path.splitext(file_name)[0]  # 获取不带扩展名的文件名

    # 创建与文件名相同的文件夹
    folder_path = os.path.join(file_dir, file_base_name)

    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            messagebox.showinfo("成功", f"文件夹 '{file_base_name}' 创建成功！")
        else:
            messagebox.showwarning("警告", f"文件夹 '{file_base_name}' 已存在！")
    except Exception as e:
        messagebox.showerror("错误", f"创建文件夹时出错: {str(e)}")

if __name__ == "__main__":
    create_folder_from_file()    