# 第六章：生成器与迭代器（深入）

---

## 6.1 迭代器协议

### 理论回顾：for 循环背后发生的三件事

第3章已经讲过可迭代对象和迭代器的基本区别，这里再深化理解。

```python
for item in [1, 2, 3]:
    print(item)
```

背后等价于：

```python
it = iter([1, 2, 3])       # 1. 调用 __iter__() 获取迭代器
while True:
    try:
        item = next(it)     # 2. 反复调用 __next__() 取值
        print(item)
    except StopIteration:   # 3. 取完抛 StopIteration → 结束
        break
```

**迭代器协议只有两个方法**：

| 方法 | 做什么 |
|------|--------|
| `__iter__()` | 返回迭代器对象自身 |
| `__next__()` | 返回下一个元素；没有就抛 `StopIteration` |

---

## 6.2 生成器——用 yield 造数据

### 理论：yield = return + 暂停 + 可恢复

普通函数用 `return` 返回值后就"死"了。生成器函数用 `yield` 返回值后只是"打个盹"，下次 `next()` 会从上次暂停的地方继续执行。

**类比**：普通函数像一次性播放的视频，看完就没了。生成器像游戏——可以在任意位置"存档"（yield），下次"读档"（next()）继续玩。

`yield` 同时做了三件事：
1. 把值返回给调用方（像 return）
2. 保存函数的执行位置
3. 交出 CPU 控制权

---

### 关键字/语法

| 关键字 | 作用 |
|--------|------|
| `yield` | 暂停并返回值，下次 `next()` 从此处继续 |
| `yield from` | 委托给另一个生成器，逐元素产出 |
| `next(g)` | 让生成器执行到下一个 yield |
| `g.send(v)` | 发一个值进生成器，同时获取下一个 yield 值 |
| `g.close()` | 关闭生成器，触发 `GeneratorExit` |
| `g.throw(e)` | 向生成器抛出异常 |

**生成器的四种状态**：

```python
import inspect

def gen():
    yield 1

g = gen()
print(inspect.getgeneratorstate(g))  # GEN_CREATED  — 刚创建
next(g)
print(inspect.getgeneratorstate(g))  # GEN_SUSPENDED — 在 yield 处暂停
# 如果耗尽或 close():
# inspect.getgeneratorstate(g)        # GEN_CLOSED
```

---

### 案例

**案例1：跟踪 yield 的执行过程——清楚看到"暂停和恢复"**

```python
def demo_yield():
    print("[生成器] 开始")
    yield "第一个"
    print("[生成器] 从第一个 yield 后恢复")
    yield "第二个"
    print("[生成器] 结束，将抛 StopIteration")

g = demo_yield()
print("创建生成器对象（还没执行函数体）")

print(">>> next(g) 第1次")
print(next(g))   # [生成器] 开始 → "第一个"

print(">>> next(g) 第2次")
print(next(g))   # 从第一个 yield 后恢复 → "第二个"

print(">>> next(g) 第3次")
# next(g) → [生成器] 结束 → StopIteration
```

**案例2：生成器改写传统的数据收集模式**

```python
# ❌ 传统：一次性返回全部结果（内存杀手）
def find_all_errors(log_path):
    errors = []
    for line in open(log_path):
        if "ERROR" in line:
            errors.append(line.strip())
    return errors   # 可能几百万条，内存爆了

# ✅ 生成器：找到一个就交出一个（内存恒定）
def find_errors_gen(log_path):
    for line in open(log_path):
        if "ERROR" in line:
            yield line.strip()
```

**案例3：yield from——消除嵌套循环**

```python
# ❌ 不用 yield from：需要双层循环
def flatten_old(nested):
    for sublist in nested:
        for item in sublist:
            yield item

# ✅ yield from：一行替代内层循环
def flatten_new(nested):
    for sublist in nested:
        yield from sublist  # 等价于 for x in sublist: yield x

data = [[1, 2], [3, 4], [5, 6]]
print(list(flatten_new(data)))  # [1, 2, 3, 4, 5, 6]
```

**案例4（工业级）：流式 ETL 管道——提取→转换→加载**

```python
import csv
from typing import Iterator, Dict

def extract_csv(path: str) -> Iterator[Dict]:
    """提取：逐行读取 CSV"""
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            yield row

def transform(records: Iterator[Dict]) -> Iterator[Dict]:
    """转换：清理和过滤"""
    for rec in records:
        if rec.get("status") != "INVALID":   # 过滤无效记录
            rec["amount"] = float(rec.get("amount", 0))
            yield rec

def load(records: Iterator[Dict], output: str) -> int:
    """加载：写入新文件"""
    count = 0
    with open(output, "w", encoding="utf-8", newline="") as f:
        first = next(records)
        writer = csv.DictWriter(f, fieldnames=list(first.keys()))
        writer.writeheader()
        writer.writerow(first)
        count = 1
        for rec in records:
            writer.writerow(rec)
            count += 1
    return count

# 管道串联：数据像水流一样依次经过每个阶段
# count = load(transform(extract_csv("input.csv")), "output.csv")
```

---

## 6.3 send()——生成器的双向通信

### 理论：生成器不仅能产出值，还能接收值

yield 可以做两件事：

```python
x = yield 产出值     # 左边：接收 send() 传入的值
                     # 右边：产出给调用方的值
```

**首次通信必须用 `next(g)` 或 `g.send(None)` 启动**——因为生成器必须执行到第一个 yield 才能接收值。

**类比**：yield 像一个服务窗口。顾客（调用方）说 `next(g)`，窗口交出当前物品。顾客说 `g.send(钱)`，窗口收下钱，同时交出下一个物品。

---

### 案例

**案例1：生成器累加器——send() 的基础用法**

```python
def accumulator():
    total = 0
    while True:
        received = yield total    # 返回 total，等待接收新值
        if received is None:
            break                 # None 表示结束
        total += received

acc = accumulator()
next(acc)              # 启动，停在 yield，返回 total=0

print(acc.send(10))    # 发送10，内部 total=10，到下一个 yield，返回 10
print(acc.send(25))    # 发送25，total=35，返回 35
print(acc.send(-5))    # 发送-5，total=30，返回 30
acc.close()            # 关闭生成器
```

**案例2：协程管道——日志过滤处理**

```python
def filter_debug(target):
    """过滤掉 DEBUG 日志，其余传给下游"""
    while True:
        log = yield
        if log["level"] != "DEBUG":
            target.send(log)

def console_writer():
    """终端输出——管道的终点"""
    while True:
        log = yield
        print(f"[{log['level']}] {log['msg']}")

# 构建管道
writer = console_writer()
next(writer)                          # 启动 writer
filter_pipe = filter_debug(writer)
next(filter_pipe)                     # 启动 filter

# 发送日志
filter_pipe.send({"level": "INFO", "msg": "服务启动"})
filter_pipe.send({"level": "DEBUG", "msg": "x=42"})    # 被过滤
filter_pipe.send({"level": "ERROR", "msg": "超时"})
```

---

## 6.4 生成器表达式 vs 列表推导式

### 理论：什么时候用圆括号？

列表推导式 `[x for x in data]` 会立即在内存中生成完整列表。生成器表达式 `(x for x in data)` 是惰性的——只有在迭代时才逐个产生值。

**选择原则**：

- 结果要多次使用 → 列表推导式
- 结果只迭代一次 + 数据量大 → 生成器表达式
- 作为函数参数（如 `sum()`）→ 生成器表达式（省略括号）

---

### 案例

**案例1：内存占用对比**

```python
import sys

lst = [x**2 for x in range(100000)]   # 存了10万个结果
gen = (x**2 for x in range(100000))   # 什么都没算，只存了个"配方"

print(sys.getsizeof(lst))  # ~800 KB
print(sys.getsizeof(gen))  # ~120 字节
```

**案例2：作为函数唯一参数，省略括号**

```python
# 完整写法
total = sum((x for x in range(100) if x % 2 == 0))

# 省略括号（只有作为唯一参数时才可以）
total = sum(x for x in range(100) if x % 2 == 0)

# 其他常见场景
max_len = max(len(w) for w in ["apple", "banana", "cherry"])
all_positive = all(x > 0 for x in [1, 3, 5])
```

**案例3：分批处理大数据——一次只加载一批**

```python
import itertools

def batch(iterable, size):
    """惰性批量分组：一次只产出 size 个"""
    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk

# 对 1000 万条数据分批次处理，每次只占 1000 条的内存
# for chunk in batch(large_dataset, batch_size=1000):
#     process(chunk)
```

---

## 本章速查

| 关键字/函数 | 作用 |
|-------------|------|
| `yield x` | 暂停，返回 x，下次 next() 从这里继续 |
| `x = yield` | 既能产出，也能接收 send() 传入的值 |
| `yield from it` | 委托子生成器，逐一产出 |
| `next(g)` | 推进生成器到下一个 yield |
| `g.send(v)` | 给生成器发值 + 推进 |
| `g.close()` | 关闭生成器 |
| `(x for x in it)` | 生成器表达式（惰性求值） |

| 一句话记忆 |
|-----------|
| 迭代器 = 能被 `next()` 的东西 |
| 生成器 = 用 `yield` 写的迭代器（最方便的写法） |
| `yield` = `return` + "下次从这里接着来" |
| 生成器表达式 = 惰性版本的列表推导式 |
