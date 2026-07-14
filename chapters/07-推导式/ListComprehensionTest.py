## 测试列表推导式普通型
ls = [x ** 2 for x in range(0, 10)]

print(ls)

## 测试列表推导式过滤型

filter_ls = [x for x in range(0, 100) if x % 2 == 0]

print(filter_ls)

## 测试列表推导式,变换型,元素数量不变if表达式写在前面
exchange_ls = ["偶数" if x % 2 == 0 else "奇数" for x in range(0, 50)]

print(exchange_ls)

## 列表推导式嵌套型(打平一个复合list)

complex_list = [[1, 2, 3], [2, 4, 6], [3, 7, 5]]

float_list = [x for row in complex_list for x in row]

print(float_list)

