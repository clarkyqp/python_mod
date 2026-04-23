import ctypes
import psutil  # 需安装：pip install psutil

def find_password_in_memory(process_name, search_str="password"):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            pid = proc.info['pid']
            break
    else:
        raise ProcessLookupError(f"未找到进程: {process_name}")

    PROCESS_VM_READ = 0x0010
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_VM_READ, False, pid)

    if not process_handle:
        raise ctypes.WinError()

    try:
        # 扫描内存（示例：查找 "password=" 后的字符串）
        MEMORY_BASIC_INFORMATION = ctypes.c_void_p * 6
        mbi = MEMORY_BASIC_INFORMATION()
        address = 0
        while ctypes.windll.kernel32.VirtualQueryEx(process_handle, address, ctypes.byref(mbi), ctypes.sizeof(mbi)):
            if mbi[0] and mbi[1] & 0x1000:  # MEM_COMMIT + PAGE_READABLE
                buffer = (ctypes.c_char * mbi[2].value)()
                bytes_read = ctypes.c_size_t()
                if ctypes.windll.kernel32.ReadProcessMemory(
                    process_handle,
                    mbi[0],
                    buffer,
                    mbi[2],
                    ctypes.byref(bytes_read)
                ):
                    memory_data = bytes(buffer).decode('utf-16le', errors='ignore')
                    if search_str in memory_data:
                        print("发现密码:", memory_data.split(search_str)[1][:50])
            address += mbi[2].value
    finally:
        ctypes.windll.kernel32.CloseHandle(process_handle)

# 示例：扫描 "解压专家.exe" 进程内存
find_password_in_memory("解压专家.exe", "password=")