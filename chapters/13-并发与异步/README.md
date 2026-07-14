# 第十三章：并发与异步

---

## 13.1 进程、线程、协程——三者的本质区别

### 理论：让程序"同时"做多件事的三种方式

**比喻——一个餐厅的解释**：

| 方式 | 类比 | 特点 |
|------|------|------|
| **多进程** | 开多家分店 | 每家店独立（内存隔离），成本高，CPU 密集型 |
| **多线程** | 同一厨房多个厨师 | 共享灶台（共享内存），I/O 密集型 |
| **协程** | 一个厨师同时做多道菜 | 切菜时等水烧开，不等，去炒另一个菜 |

**GIL（全局解释器锁）**：CPython 有一把大锁，同一时刻只允许一个线程执行 Python 字节码。所以多线程对**计算密集型**任务没用（甚至会变慢），但对 **I/O 密集型**（网络请求、文件读写）有用——因为 I/O 等待时 GIL 会释放。

**选择原则**：

- CPU 密集型（大量计算）→ **多进程**
- I/O 密集型（网络请求、数据库查询）→ **多线程**（简单）或 **asyncio**（高并发）
- 高并发网络服务 → **asyncio**

---

### 关键字/语法

```python
# 线程
import threading
t = threading.Thread(target=func, args=(arg1,))
t.start()
t.join()           # 等待线程结束

# 线程锁
lock = threading.Lock()
with lock:
    # 临界区——同一时刻只有一个线程能执行这里

# 线程池（推荐——自动管理线程生命周期）
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=5) as pool:
    future = pool.submit(func, arg)
    results = pool.map(func, items)

# 进程池
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor(max_workers=4) as pool:
    results = pool.map(func, items)

# 协程
import asyncio
async def main():
    await asyncio.gather(task1(), task2())
asyncio.run(main())
```

---

### 案例

**案例1：GIL 的存在——多线程 CPU 计算反而更慢**

```python
import time, threading

def cpu_work():
    total = 0
    for _ in range(3_000_000):
        total += 1

# 单线程
start = time.perf_counter()
cpu_work(); cpu_work()
print(f"串行: {time.perf_counter() - start:.2f}s")

# 多线程（CPU 密集型——GIL 导致比串行还慢！）
start = time.perf_counter()
t1 = threading.Thread(target=cpu_work)
t2 = threading.Thread(target=cpu_work)
t1.start(); t2.start()
t1.join(); t2.join()
print(f"多线程: {time.perf_counter() - start:.2f}s")  # 可能更慢！
```

**案例2：线程池——并发下载（I/O 密集型，线程的正确场景）**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download(url):
    time.sleep(0.5)  # 模拟网络 I/O
    return f"{url} 下载完成"

urls = [f"file_{i}.txt" for i in range(10)]
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = {pool.submit(download, url): url for url in urls}
    for future in as_completed(futures):
        print(future.result())
```

**案例3：竞态条件——为什么需要锁**

```python
import threading

# ❌ 无锁：结果不确定（每次运行结果不同）
counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1   # 不是原子操作！可被打断

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(f"无锁: {counter}")  # 期望 500000，实际少很多

# ✅ 有锁：每次运行结果一致
counter = 0
lock = threading.Lock()

def increment_safe():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1   # 原子执行
```

**案例4：asyncio——协程并发**

```python
import asyncio

async def fetch(name, delay):
    print(f"{name} 开始")
    await asyncio.sleep(delay)   # 非阻塞！让出控制权
    print(f"{name} 完成")
    return name

async def main():
    # 三个任务并发执行，总耗时约等于最慢的那个
    results = await asyncio.gather(
        fetch("任务A", 1),
        fetch("任务B", 1),
        fetch("任务C", 1),
    )
    print(results)

# asyncio.run(main())  # 总耗时约1秒（不是3秒）
```

---

## 本章速查

| 场景 | 工具 | 关键 API |
|------|------|----------|
| CPU 并行 | ProcessPoolExecutor | `pool.map(func, items)` |
| I/O 并发（简单） | ThreadPoolExecutor | `pool.submit(func, arg)` |
| 高并发网络 | asyncio | `async/await`, `gather()` |
| 线程安全 | Lock | `with lock:` |
| 并发数控制 | Semaphore | `asyncio.Semaphore(n)` |

| 一句话 | 说明 |
|--------|------|
| GIL | 同一时刻只有一个线程执行 Python 字节码 |
| 多线程适合 I/O | I/O 等待时 GIL 释放，所以有效 |
| 多进程适合 CPU | 每个进程独立 GIL，真正并行 |
| 协程 | 单线程内协作式多任务，await 处让出 |
