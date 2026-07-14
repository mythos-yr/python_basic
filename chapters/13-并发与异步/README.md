# 第十三章：并发与异步

---

## 13.1 进程、线程、协程——三种并发的本质区别

### 理论：用餐厅做类比

| 方式 | 类比 | 特点 | 适合 |
|------|------|------|------|
| **多进程** | 开多家分店 | 完全隔离（内存独立），成本高 | CPU 密集型 |
| **多线程** | 同厨房多个厨师 | 共享内存，需协调 | I/O 密集型 |
| **协程** | 一个厨师同时做多道菜 | 单线程，await 处主动让出 | 高并发网络 |

**GIL（全局解释器锁）**：CPython 有一把大锁，同一时刻只允许一个线程执行 Python 字节码。所以：
- 多线程对 **CPU 密集型**无效（甚至更慢——线程切换有开销）
- 多线程对 **I/O 密集型**有效——因为 I/O 等待时 GIL 会释放

**选择原则**：CPU 密集型 → 多进程；I/O 密集型 → 多线程或 asyncio。

---

## 13.2 多线程 (threading)

### 关键字/语法

```python
import threading

t = threading.Thread(target=func, args=(arg1, arg2))
t.start()                    # 启动线程（非阻塞，立即返回）
t.join()                     # 等待线程结束
t.is_alive()                 # 线程是否还活着

lock = threading.Lock()
with lock:                   # 获取锁（同一时刻只有一个线程能进）
    # 临界区
    pass

# 线程池（推荐——自动管理线程生命周期）
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as pool:
    future = pool.submit(func, arg)       # 提交单个任务
    results = pool.map(func, items)       # 批量提交，结果保持顺序
```

---

### 案例

**案例1：创建和等待线程**

```python
import threading, time

def worker(name, delay):
    print(f"{name} 开始")
    time.sleep(delay)
    print(f"{name} 完成")

t1 = threading.Thread(target=worker, args=("A", 0.5))
t2 = threading.Thread(target=worker, args=("B", 0.3))
t1.start(); t2.start()
t1.join(); t2.join()   # 等待两个都完成
print("全部完成")
```

**案例2：竞态条件——为什么需要锁**

```python
# ❌ 无锁：结果每次运行不同
counter = 0
def increment():
    global counter
    for _ in range(100_000):
        counter += 1    # 不是原子操作！

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()
print(counter)  # 期望 500000，实际可能少很多

# ✅ 用锁：结果确定
counter = 0; lock = threading.Lock()
def increment_safe():
    global counter
    for _ in range(100_000):
        with lock: counter += 1   # 原子执行
```

**案例3（工业级）：ThreadPoolExecutor 并发下载**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def download(url):
    time.sleep(0.5)  # 模拟 I/O
    return f"{url} → OK"

urls = [f"file_{i}" for i in range(10)]
with ThreadPoolExecutor(max_workers=3) as pool:
    futures = {pool.submit(download, u): u for u in urls}
    for future in as_completed(futures):   # 按完成顺序处理
        print(future.result())
```

---

## 13.3 多进程 (multiprocessing)

### 理论：每个进程有独立 GIL，真正并行

多进程适合 CPU 密集型计算（大量数学运算、图像处理等）。进程间通信比线程间通信开销大。

---

### 关键字/语法

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:
    results = pool.map(func, items)     # 同 ThreadPoolExecutor 的用法
```

---

### 案例

**案例1：多线程 vs 多进程——CPU 密集型对比**

```python
import math, time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def count_primes(n):
    def is_prime(x):
        for i in range(2, int(math.sqrt(x))+1):
            if x % i == 0: return False
        return x >= 2
    return sum(1 for x in range(n, n+10000) if is_prime(x))

nums = [i*10000 for i in range(8)]

# 多线程（受 GIL 限制——慢）
start = time.perf_counter()
with ThreadPoolExecutor(4) as p:
    list(p.map(count_primes, nums))
print(f"多线程: {time.perf_counter()-start:.2f}s")

# 多进程（绕过 GIL——快）
start = time.perf_counter()
with ProcessPoolExecutor(4) as p:
    list(p.map(count_primes, nums))
print(f"多进程: {time.perf_counter()-start:.2f}s")
```

---

## 13.4 异步编程 (asyncio)

### 理论：单线程 + 事件循环 = 高并发

asyncio 在单线程内通过事件循环调度协程。遇到 `await` 时，协程主动让出控制权，事件循环切换到另一个就绪的协程。适合大量网络 I/O 场景。

---

### 关键字/语法

```python
import asyncio

async def coroutine():      # async def 定义协程
    await something()        # await 暂停当前协程，让出控制权

asyncio.run(main())          # Python 3.7+ 启动事件循环
results = await asyncio.gather(task1(), task2())  # 并发运行
task = asyncio.create_task(coro())  # 创建 Task（立即提交到事件循环）
sem = asyncio.Semaphore(n)  # 控制并发数
```

---

### 案例

**案例1：同步 vs 异步——时间差 3 倍**

```python
import asyncio, time

# 同步（串行）：3s
def sync():
    for i in range(3):
        time.sleep(1)

# 异步（并发）：1s
async def async_main():
    await asyncio.gather(*[asyncio.sleep(1) for _ in range(3)])

# asyncio.run(async_main())  # 1s 完成
```

**案例2（工业级）：asyncio + Semaphore 控制并发数**

```python
import asyncio

async def fetch(sem, url):
    async with sem:                         # 控制并发数
        await asyncio.sleep(0.5)            # 模拟网络请求
        return f"{url} done"

async def main():
    sem = asyncio.Semaphore(3)              # 最多 3 个并发
    tasks = [fetch(sem, f"url_{i}") for i in range(10)]
    results = await asyncio.gather(*tasks)
    return results

# asyncio.run(main())  # 10个请求，3个并发 → 0.5×4 ≈ 2s
```

---

## 本章速查

| 场景 | 工具 | API |
|------|------|-----|
| CPU 并行 | ProcessPoolExecutor | `pool.map(func, items)` |
| I/O 并发（简单） | ThreadPoolExecutor | `pool.submit(func, arg)` |
| 高并发网络 | asyncio | `async/await`, `gather()` |
| 线程安全 | Lock | `with lock:` |
| 并发控制 | Semaphore | `asyncio.Semaphore(n)` |

| 记忆 |
|------|
| GIL：同一时刻只有一个线程执行 Python 字节码 |
| 线程 I/O 有效：I/O 等待时 GIL 释放 |
| 进程 CPU 有效：各自有独立 GIL |
| 协程：单线程内协作式调度 |
