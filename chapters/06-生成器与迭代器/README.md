# 第六章：生成器与迭代器（深入）

> 上一章学了"能用 for 循环的都是可迭代对象"。这一章深入理解生成器——Python 最强大的特性之一。

---

## 6.1 生成器函数

### 知识点：yield 的工作原理

**案例1：用调试代码跟踪 yield 的执行过程**

```python
def demo_yield():
    """用 print 跟踪生成器的执行——清楚的看到暂停和恢复"""
    print("[生成器] 开始执行")
    yield "第1个结果"
    print("[生成器] 从第1个 yield 之后恢复")
    yield "第2个结果"
    print("[生成器] 从第2个 yield 之后恢复")
    yield "第3个结果"
    print("[生成器] 函数结束，自动抛出 StopIteration")

# 调用生成器函数 → 返回生成器对象，不执行函数体！
gen = demo_yield()
print("生成器对象已创建，但函数体还没执行")
print(f"类型: {type(gen)}\n")

# 每次 next() 才执行到下一个 yield
print(">>> 第1次 next()")
result = next(gen)
print(f"收到: {result}\n")

print(">>> 第2次 next()")
result = next(gen)
print(f"收到: {result}\n")

print(">>> 第3次 next()")
result = next(gen)
print(f"收到: {result}\n")

print(">>> 第4次 next()")
try:
    next(gen)
except StopIteration:
    print("StopIteration！生成器耗尽了")
```

**案例2：用生成器改写传统的数据处理函数**

```python
# ❌ 传统写法：一次性加载所有数据
def find_errors_traditional(log_file):
    errors = []
    for line in open(log_file):
        if "ERROR" in line:
            errors.append(line.strip())
    return errors   # 可能返回百万条——内存爆炸

# ✅ 生成器写法：找到一个给一个
def find_errors_generator(log_file):
    for line in open(log_file):
        if "ERROR" in line:
            yield line.strip()   # 产生一个，暂停，等下次要

# 使用
# for error in find_errors_generator("huge_file.log"):
#     print(error)   # 内存中始终只有当前这一条
```

**案例3：工业级 —— 流式 ETL 处理管道**

```python
import csv
from typing import Iterator, Dict, List
from pathlib import Path

class StreamingETL:
    """
    流式 ETL 管道。每个阶段都是生成器，数据像水流一样依次经过。
    永远不会把全部数据加载到内存中。
    """

    @staticmethod
    def extract(filepath: str) -> Iterator[Dict]:
        """E: Extract —— 从 CSV 读取，逐行产出字典"""
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield row

    @staticmethod
    def transform(records: Iterator[Dict]) -> Iterator[Dict]:
        """T: Transform —— 清洗和转换每条记录"""
        for rec in records:
            # 去除字段两边空白
            cleaned = {k.strip(): v.strip() for k, v in rec.items()}
            # 金额转为浮点数
            if "amount" in cleaned:
                cleaned["amount"] = float(cleaned["amount"])
            # 过滤无效记录
            if cleaned.get("status") != "INVALID":
                yield cleaned

    @staticmethod
    def load(records: Iterator[Dict], output_path: str) -> int:
        """L: Load —— 写入目标文件，返回写入行数"""
        count = 0
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            if not records:
                return 0
            # 用第一行获取字段名
            first = next(records)
            writer = csv.DictWriter(f, fieldnames=list(first.keys()))
            writer.writeheader()
            writer.writerow(first)
            count = 1
            for rec in records:
                writer.writerow(rec)
                count += 1
        return count

    @classmethod
    def run_pipeline(cls, input_path: str, output_path: str) -> int:
        """运行完整管道：Extract → Transform → Load"""
        extracted = cls.extract(input_path)
        transformed = cls.transform(extracted)
        return cls.load(transformed, output_path)
```

---

### 知识点：生成器的状态

**案例1：检查生成器的四种状态**

```python
import inspect

def my_generator():
    print("starting")
    yield 1
    print("middle")
    yield 2
    print("ending")

gen = my_generator()

# GEN_CREATED: 刚创建，等待第一次执行
print(f"创建后: {inspect.getgeneratorstate(gen)}")

# GEN_SUSPENDED: 在 yield 处暂停
next(gen)
print(f"第1个 yield 后: {inspect.getgeneratorstate(gen)}")

next(gen)
print(f"第2个 yield 后: {inspect.getgeneratorstate(gen)}")

# GEN_CLOSED: 执行完毕或手动关闭
try:
    next(gen)
except StopIteration:
    print(f"耗尽后: {inspect.getgeneratorstate(gen)}")

# 对比：手动关闭
gen2 = my_generator()
next(gen2)                 # 推进到第一个 yield
print(f"暂停中: {inspect.getgeneratorstate(gen2)}")
gen2.close()               # 手动关闭
print(f"close 后: {inspect.getgeneratorstate(gen2)}")
```

**案例2：send() —— 双向通信**

```python
def echo_with_count():
    """接收值、累加、返回累加结果"""
    total = 0
    while True:
        received = yield total        # ← 返回 total，等待接收新值
        if received is None:
            break                     # 收到 None 表示停止
        total += received
        print(f"  累加: +{received} = {total}")

# 使用流程
acc = echo_with_count()
next(acc)                    # 启动生成器，停在第一个 yield，返回 total=0

print(">>> 发送 10")
result = acc.send(10)        # 发送10，生成器内部 total=10，运行到下一个 yield，返回10
print(f"返回: {result}")

print(">>> 发送 25")
result = acc.send(25)
print(f"返回: {result}")

print(">>> 发送 -5")
result = acc.send(-5)
print(f"返回: {result}")

# close() 结束生成器
acc.close()
```

**案例3：工业级 —— 协程风格的日志管线**

```python
from typing import Generator, Any
from datetime import datetime

# 定义数据处理器（协程）
def filter_debug(target: Generator) -> Generator:
    """过滤掉 DEBUG 级别的日志"""
    while True:
        log_entry = yield
        if log_entry["level"] != "DEBUG":
            target.send(log_entry)

def add_timestamp(target: Generator) -> Generator:
    """给日志加上时间戳"""
    while True:
        log_entry = yield
        log_entry["timestamp"] = datetime.now().isoformat()
        target.send(log_entry)

def console_writer() -> Generator:
    """输出到控制台"""
    while True:
        log_entry = yield
        print(f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}")


def build_pipeline() -> Generator:
    """
    构建协程管道：filter → timestamp → writer
    利用 send() 在协程间传递数据
    """
    writer = console_writer()
    next(writer)  # 启动

    timer = add_timestamp(writer)
    next(timer)   # 启动

    filter_pipe = filter_debug(timer)
    next(filter_pipe)  # 启动

    return filter_pipe  # 返回管道的入口


# 使用
pipe = build_pipeline()

pipe.send({"level": "INFO", "message": "服务启动"})
pipe.send({"level": "DEBUG", "message": "内部状态: x=42"})  # 被 filter 拦截
pipe.send({"level": "ERROR", "message": "连接超时"})
pipe.send({"level": "WARNING", "message": "磁盘使用率 90%"})

pipe.close()
```

---

### 知识点：yield from —— 委托子生成器

**案例1：yield from 消除嵌套循环**

```python
# ❌ 不用 yield from：双层 for 循环
def flatten_old(nested):
    """展开嵌套列表，需要手动遍历子列表"""
    for sublist in nested:
        for item in sublist:
            yield item

# ✅ 用 yield from：一行替代内层循环
def flatten_new(nested):
    for sublist in nested:
        yield from sublist     # 等价于 for x in sublist: yield x

data = [[1, 2], [3, 4], [5, 6]]
print(list(flatten_old(data)))   # [1, 2, 3, 4, 5, 6]
print(list(flatten_new(data)))   # [1, 2, 3, 4, 5, 6]
```

**案例2：yield from 完全展开任意嵌套结构**

```python
def deep_flatten(nested):
    """递归展开任意深度的嵌套结构"""
    for item in nested:
        # 如果是可迭代对象（且不是字符串），递归展开
        if isinstance(item, (list, tuple)):
            yield from deep_flatten(item)
        else:
            yield item

data = [1, [2, [3, 4], 5], 6, [7, 8]]
print(list(deep_flatten(data)))
# [1, 2, 3, 4, 5, 6, 7, 8]
```

**案例3：工业级 —— 文件行数统计器（yield from 委托）**

```python
import os
from pathlib import Path
from typing import Iterator, Tuple

class FileScanner:
    """
    文件扫描器——yield from 在目录遍历中的应用。
    每个子目录的遍历委托给独立的生成器，外层 yield from 组合。
    """

    @staticmethod
    def scan_directory(directory: str, pattern: str = "*") -> Iterator[Path]:
        """扫描目录，逐文件产出 Path 对象"""
        for entry in Path(directory).glob(pattern):
            if entry.is_file():
                yield entry

    @staticmethod
    def scan_recursive(root: str, pattern: str = "*.py") -> Iterator[Path]:
        """
        递归扫描目录树。
        用 yield from 委托子目录的扫描任务。
        """
        root_path = Path(root)
        for entry in root_path.iterdir():
            if entry.name.startswith("."):
                continue
            if entry.is_file() and entry.match(pattern):
                yield entry
            elif entry.is_dir():
                # yield from: 把子目录的遍历委托出去
                # 外层不需要关心每一层是怎么遍历的
                yield from FileScanner.scan_recursive(str(entry), pattern)

    @staticmethod
    def count_lines(filepath: Path) -> int:
        """统计单个文件的行数（不含空行）"""
        with open(filepath, encoding="utf-8", errors="ignore") as f:
            return sum(1 for line in f if line.strip())

    @classmethod
    def generate_report(cls, root: str) -> Iterator[Tuple[str, int]]:
        """
        生成文件行数报告（生成器——不一次性返回全部结果）。
        产出: (文件路径, 行数)
        """
        for filepath in cls.scan_recursive(root):
            count = cls.count_lines(filepath)
            yield (str(filepath), count)


# 使用
# scanner = FileScanner()
# total = 0
# for path, lines in scanner.generate_report("./my_project"):
#     print(f"{path}: {lines} 行")
#     total += lines
# print(f"\n总计: {total} 行")
```

---

## 6.2 生成器表达式

**案例1：生成器表达式与列表推导式的内存差异**

```python
import sys

# 列表推导式：立即分配内存
lst_comp = [x ** 2 for x in range(10000)]
print(f"列表推导式: {sys.getsizeof(lst_comp):,} bytes")

# 生成器表达式：几乎不占内存
gen_expr = (x ** 2 for x in range(10000))
print(f"生成器表达式: {sys.getsizeof(gen_expr):,} bytes")

# 对于大数据量，差异是质的变化
# lst_comp_big = [x ** 2 for x in range(10**9)]   # 内存不够！
gen_expr_big = (x ** 2 for x in range(10**9))       # 完全没问题
```

**案例2：生成器表达式作为函数参数（省略括号）**

```python
# 列表推导式（立即求值，需要内存存储中间结果）
total = sum([x for x in range(100) if x % 2 == 0])

# 生成器表达式（惰性求值，省去中间列表）
total = sum(x for x in range(100) if x % 2 == 0)  # 注意：省略了括号

# 其他常见用法
max_value = max(len(w) for w in ["apple", "banana", "cherry"])
all_positive = all(x > 0 for x in [1, 3, 5, -1])    # 短路！遇到 -1 就停
any_match = any("python" in line.lower() for line in open("README.md"))

print(f"最长单词长度: {max_value}")
print(f"全正: {all_positive}")
```

**案例3：工业级 —— 内存友好的批处理**

```python
import itertools
from typing import Iterator, List, TypeVar

T = TypeVar("T")

def batch(iterable, batch_size: int) -> Iterator[List[T]]:
    """
    将可迭代对象分成固定大小的批次（惰性）。
    处理百万级数据时，每次只在内存中保持一个批次。

    参考: itertools.batched (Python 3.12+)
    """
    iterator = iter(iterable)
    while True:
        batch = list(itertools.islice(iterator, batch_size))
        if not batch:
            break
        yield batch


# 模拟 1000 万条记录的处理
def generate_large_dataset(n: int):
    """模拟大数据源"""
    for i in range(n):
        yield {"id": i, "value": f"data_{i}"}

# 分批次处理，每次只在内存中保留 1000 条
total_processed = 0
for data_batch in batch(generate_large_dataset(1_000_000), batch_size=1000):
    # 在这里处理这一批数据
    total_processed += len(data_batch)

print(f"处理了 {total_processed:,} 条记录")
# 内存高峰 = 1000 条 × 每条几十字节 ≈ 几十 KB
```

---

## 6.3 无限序列与 itertools

**案例1：生成器创建无限序列**

```python
def fibonacci():
    """无限斐波那契数列"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 用 islice 取前 10 个
from itertools import islice
print(list(islice(fibonacci(), 10)))
# [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**案例2：itertools 常用工具**

```python
import itertools

# count: 无限计数器
counter = itertools.count(start=10, step=2)
print([next(counter) for _ in range(5)])  # [10, 12, 14, 16, 18]

# cycle: 无限循环
for i, item in enumerate(itertools.cycle(["A", "B", "C"])):
    print(item, end=" ")
    if i >= 8:
        break
print()  # A B C A B C A B C

# chain: 串联多个可迭代对象
print(list(itertools.chain([1, 2], [3, 4], "AB")))
# [1, 2, 3, 4, 'A', 'B']

# combinations: 组合
print(list(itertools.combinations("ABC", 2)))
# [('A', 'B'), ('A', 'C'), ('B', 'C')]

# permutations: 排列
print(list(itertools.permutations("ABC", 2)))
# [('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]

# product: 笛卡尔积
print(list(itertools.product("AB", "12")))
# [('A', '1'), ('A', '2'), ('B', '1'), ('B', '2')]
```

**案例3：工业级 —— 滑动窗口日志分析**

```python
from collections import deque
from itertools import islice
from typing import Iterator, List, TypeVar
from datetime import datetime, timedelta

T = TypeVar("T")

def sliding_window(iterable, window_size: int) -> Iterator[tuple]:
    """
    滑动窗口生成器。
    例: list(sliding_window([1,2,3,4,5], 3))
        → [(1,2,3), (2,3,4), (3,4,5)]
    """
    iterator = iter(iterable)
    window = deque(islice(iterator, window_size), maxlen=window_size)
    if len(window) == window_size:
        yield tuple(window)
    for item in iterator:
        window.append(item)
        yield tuple(window)


# 使用场景：检测日志中的异常模式
def detect_anomaly(log_records: Iterator[dict], error_threshold: int = 3):
    """
    滑动窗口检测：如果在某个窗口内错误数超过阈值，触发告警。
    """
    for window in sliding_window(log_records, window_size=10):
        error_count = sum(1 for r in window if r["level"] == "ERROR")
        if error_count >= error_threshold:
            first_ts = window[0]["timestamp"]
            last_ts = window[-1]["timestamp"]
            print(f"⚠️ 告警: {first_ts} ~ {last_ts} 之间出现 {error_count} 个错误")
            yield window


# 模拟日志流
def mock_log_stream():
    import random
    random.seed(42)
    ts = datetime.now()
    for i in range(100):
        level = "ERROR" if random.random() < 0.3 else "INFO"
        yield {"timestamp": ts, "level": level, "msg": f"event_{i}"}
        ts += timedelta(seconds=1)

# for anomaly_window in detect_anomaly(mock_log_stream(), error_threshold=5):
#     pass  # 在这里发送告警邮件、短信等
```

---

## 本章速查

| 操作 | 说明 |
|------|------|
| `yield x` | 暂停，返回 x，下次从这里继续 |
| `x = yield` | 接收 send() 传入的值 |
| `yield from it` | 委托子生成器，等价 `for x in it: yield x` |
| `g.send(v)` | 向生成器传入 v，获取下一个 yield 值 |
| `g.throw(e)` | 向生成器中抛出异常 |
| `g.close()` | 关闭生成器，触发 GeneratorExit |
| `(x for x in it)` | 生成器表达式，惰性求值 |
| `inspect.getgeneratorstate(g)` | 查看生成器状态 |

| 何时用生成器 | 场景 |
|-------------|------|
| 数据量 > 内存 | 大文件、数据流、日志处理 |
| 数据源是无限的 | 传感器数据、消息队列、用户输入 |
| 数据需要逐条处理 | ETL 管道、逐行过滤 |
| 需要惰性求值 | 避免不必要的计算 |
