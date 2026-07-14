import sys

# 测试生成器表达式性能
ls = [x ** 2 for x in range(1, 100000)]
print(sys.getsizeof(ls))
gen = (x ** 2 for x in range(1, 100000))
print(sys.getsizeof(gen))
for x in gen:
    print(x)