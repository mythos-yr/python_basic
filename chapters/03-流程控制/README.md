# 第三章：程序流程控制

---

## 3.1 条件判断

### 理论：程序需要"做选择"

程序不可能永远是一条直线执行到底。你需要告诉它："如果满足条件A，做这件事；否则做那件事"。这就是条件判断。

Python 的判断逻辑靠**真值测试**：任何对象都可以被判定为 True 或 False。

**哪些值是 False？** 记住这 8 个就够了：

```
False, None, 0, 0.0, "", [], {}, set(), ()
```

其余**一切都是 True**（包括负数、含空格的字符串 `" "`、含 None 的列表 `[None]`）。

---

### 关键字/语法

```python
if 条件:
    # 条件为 True 时执行
elif 另一个条件:
    # 上一个不满足，这个满足时执行
else:
    # 以上都不满足时执行
```

| 关键字 | 作用 |
|--------|------|
| `if` | 判断的起点 |
| `elif` | "否则如果..."（可以有多个） |
| `else` | "以上都不满足"（最多一个） |
| `match/case` | 模式匹配（Python 3.10+），比 if-elif 更强大 |
| `条件 if X else Y` | 三元表达式：条件为 True 返回 X，否则 Y |

**Python 特有的链式比较**：

```python
if 18 <= age <= 60:  # 等价于 age >= 18 and age <= 60
    print("成年人")
```

---

### 案例

**案例1：真值测试——哪些是 False**

```python
falsy = [False, None, 0, 0.0, "", [], {}, set(), ()]
for v in falsy:
    print(f"{repr(v):>10} → {bool(v)}")   # 全都是 False

print(bool(-1))        # True
print(bool(" "))       # True（空格不是空字符串！）
```

**案例2：match/case 替代复杂 if-elif（Python 3.10+）**

```python
# 传统 if-elif
def handle(event):
    if event["type"] == "click":
        return f"点击 ({event['x']}, {event['y']})"
    elif event["type"] == "keypress":
        return f"按下 {event['key']}"

# match/case：更清晰、更强大
def handle_v2(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"点击 ({x}, {y})"
        case {"type": "keypress", "key": key}:
            return f"按下 {key}"
        case _:
            return "未知事件"
```

**案例3：用字典替代长 if-elif 链（设计模式）**

```python
# ❌ 长 if-elif
def calculate(a, op, b):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    # ... 没完没了

# ✅ 操作字典（新增操作只需加一行）
operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else float("nan"),
}
print(operations["+"](3, 5))  # 8
```

---

## 3.2 循环

### 理论：让计算机重复做一件事

循环分两种思路：

- **while**：当条件为真时一直做（不知道要做多少次）
- **for**：对一个集合里的每个元素各做一次（知道有多少个）

**for 循环的本质**：Python 的 `for` 不是 C 语言那样"数数循环"，它是**对可迭代对象中的每个元素执行**。底层靠迭代器协议实现：先调 `iter()` 取迭代器，再反复调 `next()`，遇到 `StopIteration` 停止。

---

### 关键字/语法

```python
# while 循环
while 条件:
    # 条件成立就一直循环
else:                  # 可选：正常结束（非 break）时执行
    pass

# for 循环
for 变量 in 可迭代对象:
    # 对每个元素执行
else:                  # 可选：正常遍历完时执行
    pass
```

| 关键字 | 作用 |
|--------|------|
| `while` | 条件循环 |
| `for` | 迭代循环 |
| `break` | 立即终止**整个**循环 |
| `continue` | 跳过本次迭代的剩余代码，进入下一轮 |
| `pass` | 什么都不做（占位符） |
| `else`（配合循环） | 循环**没有被 break** 时才执行 |

**while/else 和 for/else 的 else 含义**：循环"善终"时才执行。被 break 打断不算善终。

---

### 案例

**案例1：for/else——搜索找到时跳过 else，没找到时执行 else**

```python
# 在列表中找偶数
def find_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            print(f"找到了: {n}")
            break         # 找到 → else 不执行
    else:
        print("没找到偶数")  # 没 break → else 执行

find_even([1, 3, 5, 7])    # 没找到偶数
find_even([1, 3, 4, 7])    # 找到了: 4
```

**案例2：用 break 替代标志变量**

```python
# ❌ 需要一个 found 变量
found = False
for item in data:
    if match(item):
        found = True
        break

# ✅ break + else 更优雅
for item in data:
    if match(item):
        break
else:
    print("没有匹配项")
```

**案例3：带重试的 while 循环（工业级模式）**

```python
import time

def retry_operation(func, max_retries=3, delay=1.0):
    """重试执行某个操作，最多重试 max_retries 次"""
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except Exception as e:
            print(f"第{attempt}次失败: {e}")
            if attempt < max_retries:
                time.sleep(delay)
    raise RuntimeError(f"重试{max_retries}次后仍然失败")

# 使用
# result = retry_operation(lambda: requests.get("https://api.example.com"))
```

---

## 3.3 可迭代对象与迭代器

### 理论：for 循环能在哪些东西上工作？

**可迭代对象 (Iterable)**：任何可以"逐个取出元素"的东西。本质上就是实现了 `__iter__()` 方法的对象——当你把它放进 for 循环时，Python 调用 `iter(obj)` 来获取一个迭代器。

**迭代器 (Iterator)**：具体的"取东西的人"。实现了 `__iter__()` + `__next__()` 方法。每调一次 `next()` 返回下一个元素，没了就抛 `StopIteration`。

**核心区别**：
- 可迭代对象：可以**多次**遍历（每次 `iter()` 都返回新的迭代器）
- 迭代器：**一次性**的，遍历完就空了

**类比**：
- 可迭代对象 = 一本书（可以反复翻开，每次从头读）
- 迭代器 = 书签（记录当前位置，只能往后翻，不能倒退，翻完就没了）

---

### 关键字/语法

| 函数 | 作用 |
|------|------|
| `iter(obj)` | 从可迭代对象获取迭代器 |
| `next(it)` | 从迭代器取下一个元素 |
| `StopIteration` | 迭代器耗尽时抛出的异常 |

---

### 案例

**案例1：for 循环的底层等价代码**

```python
# for item in [1, 2, 3]:
#     print(item)
#
# 完全等价于：

it = iter([1, 2, 3])
while True:
    try:
        item = next(it)
        print(item)
    except StopIteration:
        break
```

**案例2：可迭代对象 vs 迭代器的区分**

```python
from collections.abc import Iterable, Iterator

lst = [1, 2, 3]
it = iter(lst)

print(isinstance(lst, Iterable))   # True —— 可以遍历
print(isinstance(lst, Iterator))   # False —— 不是迭代器本身
print(isinstance(it, Iterable))    # True —— 迭代器也可以遍历
print(isinstance(it, Iterator))    # True —— 是迭代器

# 关键差异：可迭代对象可以多次遍历，迭代器只能一次
print(list(lst))  # [1, 2, 3]
print(list(lst))  # [1, 2, 3] —— 第二次还是全的

print(list(it))   # [1, 2, 3]
print(list(it))   # [] —— 第一次就耗尽了！
```

**案例3：自定义一个可倒数的迭代器**

```python
class Countdown:
    """倒计时迭代器——理解 __iter__ 和 __next__"""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self           # 迭代器的 __iter__ 返回自己

    def __next__(self):
        if self.current < 0:
            raise StopIteration  # 没了！终止
        val = self.current
        self.current -= 1
        return val

for n in Countdown(3):
    print(n)  # 3, 2, 1, 0
```

---

## 本章速查

| 结构 | 说明 |
|------|------|
| `if/elif/else` | 条件判断，支持链式比较 `0 < x < 10` |
| `match/case` | 模式匹配（3.10+） |
| `while` | 条件循环，`while/else` 非 break 退出执行 else |
| `for` | 迭代循环，`for/else` 未被 break 打断时执行 else |
| `break` | 终止整个循环 |
| `continue` | 跳过本次迭代剩余代码 |
| `pass` | 什么都不做的占位语句 |
| 可迭代对象 | 有 `__iter__`，可以多次遍历 |
| 迭代器 | 有 `__iter__` + `__next__`，一次性 |
