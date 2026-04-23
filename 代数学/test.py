# 方法1：直接计算
num1 = int('1' * 23)
num2 = int('1' * 41)

product = num1 * num2

print(f"第一个数 (23个1): {num1}")
print(f"第二个数 (41个1): {num2}")
print(f"\n乘积: {product}")
print(f"\n乘积的位数: {len(str(product))}")

# 方法2：使用数学公式推导（可选）
# 由n个1组成的数可以表示为：(10^n - 1)/9
num1_alt = (10**23 - 1) // 9
num2_alt = (10**41 - 1) // 9
product_alt = num1_alt * num2_alt

print(f"\n验证 (使用公式计算):")
print(f"两个结果是否相同: {product == product_alt}")

# 展示乘积的部分位数
product_str = str(product)
print(f"\n乘积的前50位: {product_str[:50]}")
print(f"乘积的后50位: {product_str[-50:]}")