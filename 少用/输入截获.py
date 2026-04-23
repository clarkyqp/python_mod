from pynput import keyboard, mouse
import threading

def on_press(key):
    try:
        print(f'按键按下: {key.char}')
    except AttributeError:
        print(f'特殊按键: {key}')

def on_release(key):
    print(f'按键释放: {key}')
    if key == keyboard.Key.esc:
        # 停止监听
        return False

def on_click(x, y, button, pressed):
    action = '按下' if pressed else '释放'
    print(f'鼠标{action} 在 ({x}, {y}) 使用 {button}')

def on_scroll(x, y, dx, dy):
    print(f'滚轮滚动 在 ({x}, {y}) 方向 {"下" if dy < 0 else "上"}')

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def start_mouse_listener():
    with mouse.Listener(on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()

if __name__ == '__main__':
    # 启动键盘和鼠标监听线程
    keyboard_thread = threading.Thread(target=start_keyboard_listener)
    mouse_thread = threading.Thread(target=start_mouse_listener)
    
    keyboard_thread.start()
    mouse_thread.start()
    
    keyboard_thread.join()
    mouse_thread.join()