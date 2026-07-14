# 第六章：生成器与迭代器（深入）

---

## 6.1 迭代器协议

### 理论：for 循环背后发生的三件事

```python
for item in [1, 2, 3]:
    print(item)
```

每一步都在发生什么：

```python
it = iter([1, 2, 3])       # ① 调用 __iter__()，获取"取东西的人"（迭代器）
while True:
    try:
        item = next(it)     # ② 反复调用 __next__()，"下一个！"
        print(item)
    except StopIteration:   # ③ 取完了，抛 StopIteration → 结束循环
        break
```

**迭代器协议只有两个方法**：

| 方法 | 做什么 | 返回值 |
|------|--------|--------|
| `__iter__()` | 返回迭代器自身 | self |
| `__next__()` | 返回下一个元素 | 下一个元素；没了抛 `StopIteration` |

**可迭代对象 vs 迭代器**：
- 可迭代对象（list、str、dict...）：有 `__iter__`，每次调用返回**新的**迭代器 → 可多次遍历
- 迭代器：有 `__iter__` + `__next__`，`__iter__` 返回自身 → **一次性**，遍历完就空了

---

### 案例

**案例1：自定义迭代器类——理解协议**

```python
class Countdown:
    """倒计时迭代器"""

    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        return self            # 迭代器自己就是"取东西的人"

    def __next__(self):
        if self.current < 0:
            raise StopIteration  # "没了！"
        value = self.current
        self.current -= 1
        return value

for n in Countdown(3):
    print(n)    # 3, 2, 1, 0

# 证明迭代器一次性：第二次遍历为空
cd = Countdown(2)
print(list(cd))   # [2, 1, 0]
print(list(cd))   # [] —— 已耗尽
```

**案例2：区分可迭代对象和迭代器**

```python
from collections.abc import Iterable, Iterator

lst = [1, 2, 3]          # 可迭代对象
it = iter(lst)             # 迭代器

print(isinstance(lst, Iterable))  # True  —— 可遍历
print(isinstance(lst, Iterator))  # False —— 但自己不是"取东西的人"
print(isinstance(it, Iterable))   # True  —— 迭代器也是可遍历的
print(isinstance(it, Iterator))   # True  —— 是"取东西的人"

# 关键区别：可迭代对象可多次遍历
print(list(lst))  # [1, 2, 3]
print(list(lst))  # [1, 2, 3]  ← 第二次还是完整的

print(list(it))   # [1, 2, 3]
print(list(it))   # []  ← 迭代器已耗尽！
```

**案例3（工业级）：分页迭代器——封装"翻页"逻辑**

```python
class PaginatedIterator:
    """自动处理分页的迭代器——调用方只需要 for 循环"""

    def __init__(self, page_fetcher, page_size=100):
        self._fetcher = page_fetcher  # 签名为 (page_num, size) -> list
        self._size = page_size
        self._page = 0
        self._current = []
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._current):   # 当前页用完了
            self._page += 1
            self._current = self._fetcher(self._page, self._size)
            self._index = 0
            if not self._current:
                raise StopIteration             # 没更多数据了
        item = self._current[self._index]
        self._index += 1
        return item

# 使用方完全不用关心分页，直接 for 循环
# for user in PaginatedIterator(lambda p, s: api.get_users(page=p, size=s)):
#     process(user)
```

---

## 6.2 生成器——用 yield 造数据

### 理论：yield = return + 暂停 + 下次从这里继续

普通函数 `return` 后函数就"死"了。生成器函数 `yield` 后只是"暂停"——下次 `next()` 从上次 yield 的下一行继续执行。

**类比**：普通函数 = 一次性播放的视频（看完就没了）。生成器 = 可以随时存档/读档的游戏。

`yield` 一次做了三件事：
1. 返回值给调用方（类似 return）
2. 保存函数的执行位置和局部变量
3. 交出 CPU 控制权

---

### 关键字/语法

| 关键字/函数 | 作用 |
|------------|------|
| `yield x` | 暂停，返回 x，下次 `next()` 从下一行继续 |
| `x = yield y` | 既能产出 y，也能接收 `send()` 传入的值 |
| `yield from it` | 委托子生成器，逐元素产出，双向透明 |
| `next(g)` | 推进到下一个 yield |
| `g.send(v)` | 给生成器发值 + 推进（首次必须 send(None) 或 next()） |
| `g.close()` | 关闭生成器，内部触发 GeneratorExit |
| `g.throw(e)` | 往生成器里抛异常 |

**生成器的四种状态**：

```python
import inspect

g = (lambda: (yield 1))()     # GEN_CREATED  刚创建，还没开始
next(g)                        # GEN_SUSPENDED 在 yield 处暂停
# 耗尽或 close()后             # GEN_CLOSED    已关闭
```

---

### 案例

**案例1：用 print 跟踪 yield——清楚看到暂停和恢复**

```python
def demo():
    print("[生成器] 开始执行")
    yield "第1个"
    print("[生成器] 从第1个 yield 后恢复")
    yield "第2个"
    print("[生成器] 函数结束，自动抛 StopIteration")

g = demo()
print(">>> 第1次 next()")
print(next(g))   # [生成器] 开始执行 → "第1个"
print(">>> 第2次 next()")
print(next(g))   # 恢复 → "第2个"
print(">>> 第3次 next()")
# next(g) → StopIteration
```

**案例2：生成器 vs 传统模式——内存差异是质变**

```python
# ❌ 传统：把所有结果收集到列表再返回——内存存不下
def get_all_errors(path):
    errors = []
    for line in open(path):
        if "ERROR" in line:
            errors.append(line.strip())
    return errors   # 百万条 → 内存爆炸

# ✅ 生成器：找到一个交一个——内存恒定不变
def stream_errors(path):
    for line in open(path):
        if "ERROR" in line:
            yield line.strip()
```

**案例3：yield from——三种等价写法**

```python
# 手动循环
def flatten_v1(nested):
    for sublist in nested:
        for item in sublist:
            yield item

# yield from 简化
def flatten_v2(nested):
    for sublist in nested:
        yield from sublist     # 等价于 for x in sublist: yield x

# 递归展开任意深度
def deep_flatten(nested):
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from deep_flatten(item)   # 递归委托
        else:
            yield item

print(list(deep_flatten([1, [2, [3, 4], 5], 6])))  # [1,2,3,4,5,6]
```

**案例4（工业级）：流式 ETL 管道——每个阶段都是生成器**

```python
import csv
from typing import Iterator, Dict

def extract(path: str) -> Iterator[Dict]:
    """E: 逐行读 CSV"""
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield row

def transform(records: Iterator[Dict]) -> Iterator[Dict]:
    """T: 清洗过滤"""
    for r in records:
        if r.get("status") != "INVALID":
            r["amount"] = float(r.get("amount", 0))
            yield r

def load(records: Iterator[Dict], output: str) -> int:
    """L: 写入目标"""
    count = 0
    with open(output, "w", newline="", encoding="utf-8") as f:
        first = next(records)
        w = csv.DictWriter(f, fieldnames=list(first.keys()))
        w.writeheader(); w.writerow(first); count = 1
        for r in records:
            w.writerow(r); count += 1
    return count

# 串联：load(transform(extract("in.csv")), "out.csv")
# 数据像水流一样经过每个阶段，从不全部加载到内存
```

---

## 6.3 send()——生成器的双向通信

### 理论：yield 既能产出也能接收

```python
received = yield output    # 左收右产
```

首次必须 `next(g)` 或 `g.send(None)` 启动（推进到第一个 yield）。之后 `g.send(x)` 将 x 传给 yield 左边的变量。

---

### 案例

**案例1：累加器——收一个值，累加，返回当前总和**

```python
def accumulator():
    total = 0
    while True:
        received = yield total
        if received is None:
            break
        total += received

acc = accumulator()
next(acc)              # 启动 → total=0

print(acc.send(10))    # +10 → 10
print(acc.send(25))    # +25 → 35
print(acc.send(-5))    # -5  → 30
acc.close()
```

**案例2：协程管道——日志处理（filter → writer）**

```python
def filter_debug(target):
    while True:
        log = yield
        if log["level"] != "DEBUG":
            target.send(log)     # 传给下游

def console_writer():
    while True:
        log = yield
        print(f"[{log['level']}] {log['msg']}")

w = console_writer(); next(w)        # 启动 writer
f = filter_debug(w); next(f)         # 启动 filter

f.send({"level": "INFO", "msg": "启动"})      # ✅ 打印
f.send({"level": "DEBUG", "msg": "x=42"})     # ❌ 被过滤
f.send({"level": "ERROR", "msg": "超时"})     # ✅ 打印
```

---

## 6.4 生成器表达式 vs 列表推导式

### 理论：方括号立即，圆括号惰性

```python
[x for x in data]   # list：立即计算，全部存内存
(x for x in data)   # generator：需要时才算，不占内存
```

| 场景 | 用什么 |
|------|--------|
| 结果要反复用 | `[...]` 列表推导式 |
| 只迭代一次 + 数据大 | `(...)` 生成器表达式 |
| 作为 `sum()`/`max()` 的参数 | 生成器（省略括号） |

---

### 案例

**案例1：内存占用天壤之别**

```python
import sys
lst = [x**2 for x in range(100000)]   # ~800 KB
gen = (x**2 for x in range(100000))   # ~120 字节
```

**案例2：作为函数唯一参数——省略括号**

```python
total = sum(x for x in range(100) if x % 2 == 0)   # 无需多一层括号
longest = max(len(w) for w in ["apple", "banana"])
all_ok = all(x > 0 for x in [1, 3, 5])             # 短路，遇到 False 就停
```

**案例3：itertools + 生成器——无限序列和批处理**

```python
import itertools

# 无限序列——用时才取
def fibonacci():
    a, b = 0, 1
    while True:
        yield a; a, b = b, a + b

first_10 = list(itertools.islice(fibonacci(), 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

# 滑动窗口——日志异常检测
def sliding_window(it, n):
    """惰性滑动窗口: [1,2,3,4] 取3 → (1,2,3) (2,3,4)"""
    from collections import deque
    window = deque(itertools.islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for item in it:
        window.append(item)
        yield tuple(window)
```

---

## 本章速查

| 关键字/函数 | 作用 |
|------------|------|
| `yield x` | 暂停，返回 x，可恢复 |
| `x = yield y` | 左收右产（双向） |
| `yield from it` | 委托子生成器 |
| `next(g)` | 推进生成器 |
| `g.send(v)` | 发值 + 推进 |
| `g.close()` | 关闭 |
| `(x for x in it)` | 生成器表达式（惰性） |

| 记忆 |
|------|
| 迭代器 = 能被 `next()` 的东西 |
| 生成器 = 用 `yield` 写的迭代器 |
| `yield` = `return` + "下次从这里接着来" |
