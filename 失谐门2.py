def find_numbers():
    """找出大于721小于30000且减去721后能被36整除的数"""
    results = []
    # 计算721 mod 36 = 1，所以我们需要找 n ≡ 1 mod 36
    # 第一个大于721的数：721 + 36 = 757
    # 最后一个小于30000的数：29964 + 1 = 29965 (因为29964 ≡ 0 mod 36)
    
    start = 757
    end = 29965
    
    # 生成所有满足条件的数
    current = start
    while current <= end:
        results.append(current)
        current += 36
    
    return results

def save_to_file(numbers, filename):
    """将带序号的数字列表保存到txt文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, num in enumerate(numbers, 1):  # 从1开始编号
            f.write(f"{i}. {num}\n")  # 格式：序号. 数字

# 主程序
if __name__ == "__main__":
    # 找出所有满足条件的数
    numbers = find_numbers()
    
    # 输出统计信息
    print(f"找到 {len(numbers)} 个满足条件的数")
    print(f"第一个数: {numbers[0]} (第1个)")
    print(f"最后一个数: {numbers[-1]} (第{len(numbers)}个)")
    
    # 保存到文件
    filename = "result_numbers.txt"
    save_to_file(numbers, filename)
    print(f"结果已保存到 {filename}")