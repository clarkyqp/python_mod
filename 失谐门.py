import math

def calculate_clicks():
    with open("door_and_fire_clicks.txt", "w", encoding="utf-8") as f:
        # 写入表头
        f.write("ID\t差值(647-ID)\tM值(差值×1.5)\t舍弃小数后的M\t火堆点击总次数\t门方向\n")
        
        # 遍历id从1到647
        for target_id in range(1, 648):
            # 计算差值
            difference = 647 - target_id
            
            # 计算M（差值×1.5）
            M = difference * (3 / 2)
            
            # 舍弃小数部分（向下取整）
            M_floor = math.floor(M)
            
            # 计算火堆点击总次数（M_floor + 4）
            clicks = M_floor + 4
            
            # 确定门的方向
            door_direction = "向左开" if target_id < 647 else "无（等于647）"
            
            # 写入结果
            f.write(f"{target_id}\t{clicks}\t{door_direction}\n")

    print("TXT文件已生成：door_and_fire_clicks.txt")

calculate_clicks()