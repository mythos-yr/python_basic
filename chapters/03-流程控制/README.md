# 第三章：程序流程控制

---

## 3.1 条件判断

### 理论：让程序"做选择"

程序不可能永远直线执行。`if` 让程序根据条件选择不同的执行路径。

Python 判断条件靠**真值测试**：任何对象都可以被判定为 True 或 False。

**哪些值是 False？** 记住这 8 个：`False, None, 0, 0.0, 0j, "", [], {}, set(), ()`。其余**一切都是 True**（包括负数、`" "`、`[None]`）。

---

### 关键字/语法

```python
if 条件:
    ...
elif 另一个条件:      # 可选，可以多个
    ...
else:                 # 可选，最多一个
    ...
```

| 关键字/语法 | 作用 |
|------------|------|
| `if` / `elif` / `else` | 条件判断 |
| `值1 if 条件 else 值2` | 三元表达式：条件 True → 值1，否则 值2 |
| `match / case` | 模式匹配（Python 3.10+），比 if-elif 更强大 |
| `0 < x < 10` | 链式比较：`0 < x and x < 10` 的简写 |

---

### 案例

**案例1：真值测试——哪些是 False，哪些容易误判**

```python
falsy = [False, None, 0, 0.0, "", [], {}, set(), ()]
for v in falsy:
    print(f"{repr(v):>10} → {bool(v)}")    # 全都是 False

# 容易误判的值
print(bool(-1))        # True  ← 负数也是 True！
print(bool(" "))       # True  ← 有空格，不是空字符串！
print(bool([None]))    # True  ← 非空列表
print(bool("False"))   # True  ← 这是字符串，不是布尔值！
```

**案例2：match/case 的多种匹配模式（Python 3.10+）**

```python
def handle(event):
    match event:
        # 字典模式：解构键值
        case {"type": "click", "x": x, "y": y}:
            return f"点击 ({x}, {y})"

        # 列表模式
        case ["quit"]:
            return "退出"
        case ["add", *items]:
            return f"添加: {items}"

        # 守卫条件（额外的 if）
        case {"type": "login", "name": name} if len(name) < 3:
            return "名字太短"

        # OR 模式
        case {"status": 200 | 201}:
            return "请求成功"

        case _:              # 默认（匹配任何）
            return "未知事件"
```

**案例3：用字典替代长 if-elif 链**

```python
# ❌ 一长串 if-elif：每加一个操作要加 2 行
# if op == "+": return a + b
# elif op == "-": return a - b ...

# ✅ 操作字典：加一个操作只需写一行
ops = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else float("nan"),
}
print(ops["*"](6, 7))  # 42
```

---

## 3.2 循环

### 理论：让计算机重复做事

- **while**：条件成立时一直做（次数不确定）
- **for**：对集合中每个元素各做一次（次数确定）

**for 循环的本质**：不是"数数循环"，而是对**可迭代对象**中每个元素依次执行。底层靠迭代器协议：`iter()` → 反复 `next()` → `StopIteration` 停止。

**`else` 配合循环**：循环**正常结束**（没有被 break 打断）时执行。常用于"找不到时做什么"的场景。

---

### 关键字/语法

| 关键字 | 作用 |
|--------|------|
| `while 条件:` | 条件循环 |
| `for x in it:` | 迭代循环 |
| `break` | 立即终止**整个**循环 |
| `continue` | 跳过本次迭代剩余代码 |
| `pass` | 什么都不做（占位符） |
| `else`（配合循环） | 循环**未被 break 打断**时执行 |

**range()——生成整数序列**：

```python
range(stop)              # 0, 1, ..., stop-1
range(start, stop)       # start, start+1, ..., stop-1
range(start, stop, step) # 带步长
```

**enumerate()——遍历时同时获取索引**：

```python
for i, item in enumerate(["a", "b", "c"]):
    print(f"{i}: {item}")   # 0: a, 1: b, 2: c

enumerate(["a","b"], start=1)  # 从 1 开始编号
```

**zip()——并行遍历多个可迭代对象**：

```python
for name, score in zip(["A","B"], [85, 92]):
    print(f"{name}: {score}")
```

---

### 案例

**案例1：for/else——搜索未找到时执行 else**

```python
def find_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            print(f"找到了: {n}")
            break              # 找到 → else 不执行
    else:
        print("没找到偶数")     # 没 break → else 执行

find_even([1, 3, 5])    # 没找到偶数
find_even([1, 3, 4])    # 找到了: 4
```

**案例2：while/else——判断质数**

```python
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            break          # 找到因子 → else 不执行
        i += 1
    else:
        return True        # 没 break → 是质数
    return False

print(is_prime(17))   # True
print(is_prime(24))   # False
```

**案例3：enumerate + zip 组合使用**

```python
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]

# zip: 并行遍历
for name, score in zip(names, scores):
    print(f"{name}: {score}")

# enumerate + zip: 带排名
for rank, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"第{rank}名: {name} ({score}分)")

# 长短不一时：zip 在最短的耗尽时停止；zip_longest 用默认值填充缺失的
from itertools import zip_longest
names2 = ["A", "B", "C", "D"]
scores2 = [90, 80]
for name, score in zip_longest(names2, scores2, fillvalue=0):
    print(f"{name}: {score}")   # D: 0
```

**案例4（工业级）：带退避策略的重试循环**

```python
import time, random

def retry_with_backoff(func, max_attempts=5, base_delay=1.0):
    """指数退避重试：第1次等1s，第2次等2s，第3次等4s..."""
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts:
                raise
            delay = base_delay * (2 ** (attempt - 1))
            jitter = random.uniform(0, delay * 0.1)  # 加随机抖动
            print(f"第{attempt}次失败: {e}，{delay+jitter:.1f}s后重试")
            time.sleep(delay + jitter)
```

---

## 3.3 可迭代对象与迭代器（入门）

### 理论：for 循环能在哪些东西上工作？

**可迭代对象 (Iterable)**：实现了 `__iter__()`，可以"逐个取出元素"。list、str、dict、set、tuple、range、文件对象都是。

**迭代器 (Iterator)**：实现了 `__iter__()` + `__next__()`，是具体"取东西的人"。每次 `next()` 取一个，取完抛 `StopIteration`。

**类比**：可迭代对象 = 一本书（可反复读），迭代器 = 书签（只能往后翻，翻完就没了）。

---

### 案例

**案例1：for 循环的底层等价代码**

```python
for item in [1, 2, 3]:
    print(item)

# 完全等价于：
it = iter([1, 2, 3])
while True:
    try:
        item = next(it)
        print(item)
    except StopIteration:
        break
```

**案例2：list 可多次遍历，迭代器只能一次**

```python
lst = [1, 2, 3]
it = iter(lst)

print(list(lst))  # [1, 2, 3] ← 第1次
print(list(lst))  # [1, 2, 3] ← 第2次，还是全的
print(list(it))   # [1, 2, 3] ← 第1次
print(list(it))   # []         ← 迭代器已耗尽！
```

**案例3：自定义倒计时迭代器**

```python
class Countdown:
    def __init__(self, start):
        self.current = start
    def __iter__(self):
        return self
    def __next__(self):
        if self.current < 0:
            raise StopIteration
        v = self.current
        self.current -= 1
        return v

for n in Countdown(3):
    print(n)  # 3, 2, 1, 0
```

---

## 本章速查

| 结构 | 说明 |
|------|------|
| `if/elif/else` | 条件判断，支持 `0 < x < 10` 链式比较 |
| `match/case` | 模式匹配（3.10+），支持解构+守卫 |
| `while/for` | 两种循环，都支持 `else` |
| `break/continue` | 终止循环 / 跳过本轮 |
| `range(start,stop,step)` | 生成整数序列 |
| `enumerate(it, start)` | 带索引遍历 |
| `zip(a, b)` | 并行遍历（最短耗尽即停） |
| 可迭代对象 | 有 `__iter__`，可多次遍历 |
| 迭代器 | 有 `__next__`，一次性 |
