from sympy import primerange

# 设定 n 和 a_4
n = 1234268228312430759578090015472355712114804731217710966738223
upper_limit = 10**5

# 筛选4k+1型素数
primes = [p for p in primerange(1, upper_limit) if p % 4 == 1]

# 这里填入选择的a_4值，小于N^(1/5)就行，最好小点
a_4 = 1
prime_base = []

# 找出符合条件的小素数
for q in primes:
    count = 0
    r = n % q
    for j in range(1, q):
        if (a_4 * (j**4)) % q == r:
            count += 1
    if count != 0:
        # print(q)
        prime_base.append(q)

# 显示生成的素数数量和前几个素数作为示例
number_of_primes, example_primes = len(prime_base), prime_base[:10]
number_of_primes, example_primes