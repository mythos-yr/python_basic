# 第十三章：并发与异步

---

## 13.1 并发基础概念

### 知识点：进程、线程、协程的区别

```
┌─────────────────────────────────────────────────────────┐
│  概念    隔离性        开销      适用场景                │
├─────────────────────────────────────────────────────────┤
│  进程    完全隔离       大       CPU 密集型（计算）       │
│  线程    共享内存       中       I/O 密集型（网络/磁盘）  │
│  协程    单线程内切换   小       高并发 I/O（网络服务）   │
└─────────────────────────────────────────────────────────┘
```

**案例1：直观理解——厨房类比**

```python
# 进程 = 独立厨房（各有各的灶台、冰箱、厨师）
# 线程 = 同一个厨房里的多个厨师（共享灶台和冰箱，需要协调）
# 协程 = 一个厨师同时做多道菜（切菜时等水烧开，不等，去干别的）
```

**案例2：三种方式的代码骨架**

```python
# 多进程：适合计算密集型
# from multiprocessing import Process, Pool

# 多线程：适合 I/O 密集型（但受 GIL 限制）
# from threading import Thread

# 异步：适合高并发 I/O
# import asyncio
```

---

## 13.2 GIL（全局解释器锁）

### 知识点：GIL 是什么、为什么、怎么办

**案例1：证明 GIL 的存在——多线程计算反而变慢**

```python
import time
import threading

def cpu_bound_task(n):
    """CPU 密集型任务"""
    count = 0
    for i in range(n):
        count += i ** 2
    return count

def run_single_thread(n):
    start = time.perf_counter()
    cpu_bound_task(n)
    return time.perf_counter() - start

def run_multi_thread(n, num_threads=4):
    start = time.perf_counter()
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=cpu_bound_task, args=(n // num_threads,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return time.perf_counter() - start

# 测试
n = 10_000_000
single_time = run_single_thread(n)
multi_time = run_multi_thread(n, num_threads=4)

print(f"单线程: {single_time:.3f}s")
print(f"多线程(4): {multi_time:.3f}s")
print(f"多线程反而{'慢' if multi_time > single_time else '快'}了！")
# 因为 GIL 导致 Python 字节码同一时刻只有一个线程在执行
```

**案例2：绕过 GIL——多进程对比多线程**

```python
import time
import math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def is_prime(n):
    """判断质数（CPU 密集型）"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def count_primes(numbers):
    return sum(1 for n in numbers if is_prime(n))

numbers = list(range(100_000, 200_000))

# 多线程（受 GIL 限制）
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=4) as pool:
    chunks = [numbers[i::4] for i in range(4)]
    results = list(pool.map(count_primes, chunks))
print(f"多线程: {time.perf_counter() - start:.2f}s, 质数: {sum(results)}")

# 多进程（绕过 GIL）
start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as pool:
    chunks = [numbers[i::4] for i in range(4)]
    results = list(pool.map(count_primes, chunks))
print(f"多进程: {time.perf_counter() - start:.2f}s, 质数: {sum(results)}")
# 多进程明显更快
```

**案例3：工业级 —— ThreadPoolExecutor 并发下载文件**

```python
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

class ConcurrentDownloader:
    """
    并发文件下载器。
    I/O 密集型任务——线程是最好的选择。
    """

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.results: Dict[str, str] = {}
        self._lock = threading.Lock()

    def download_one(self, url: str) -> str:
        """模拟下载单个文件"""
        # 实际开发中: response = requests.get(url, timeout=30)
        time.sleep(0.5)  # 模拟网络延迟
        return f"[{url}] 的内容"  # response.text

    def download_all(self, urls: List[str]) -> Dict[str, str]:
        """
        并发下载所有文件。
        线程池自动管理线程的创建和回收。
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_url = {
                executor.submit(self.download_one, url): url
                for url in urls
            }

            # 按完成顺序获取结果
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    content = future.result()
                    with self._lock:
                        self.results[url] = content
                        print(f"✅ 完成: {url}")
                except Exception as e:
                    print(f"❌ 失败: {url} — {e}")

        return self.results


# 使用
urls = [f"https://example.com/file{i}.txt" for i in range(10)]
downloader = ConcurrentDownloader(max_workers=3)
# results = downloader.download_all(urls)
# print(f"下载了 {len(results)} 个文件")
```

---

## 13.3 线程安全

### 知识点：Lock 与竞态条件

**案例1：没有锁的后果——竞态条件**

```python
import threading

# ❌ 无锁：结果不确定
counter_no_lock = 0

def increment_no_lock():
    global counter_no_lock
    for _ in range(100000):
        counter_no_lock += 1   # 这不是原子操作！

threads = []
for _ in range(10):
    t = threading.Thread(target=increment_no_lock)
    threads.append(t)
    t.start()
for t in threads:
    t.join()

print(f"无锁结果: {counter_no_lock}")  # 期望 1000000，实际可能少很多
```

**案例2：用 Lock 解决竞态条件**

```python
import threading

# ✅ 有锁：结果确定
counter_locked = 0
lock = threading.Lock()

def increment_locked():
    global counter_locked
    for _ in range(100000):
        with lock:                      # acquire + release 自动管理
            counter_locked += 1         # 临界区：同一时刻只有一个线程能执行

threads = []
for _ in range(10):
    t = threading.Thread(target=increment_locked)
    threads.append(t)
    t.start()
for t in threads:
    t.join()

print(f"有锁结果: {counter_locked}")  # 精确 1000000
```

**案例3：工业级 —— 线程安全的连接池**

```python
import threading
import time
import random
from queue import Queue
from typing import List, Optional

class ConnectionPool:
    """
    简易数据库连接池（线程安全）。
    演示 Lock 和 Queue 的实际应用。
    """

    def __init__(self, create_connection, pool_size: int = 5):
        self._create = create_connection
        self._pool = Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_count = 0

        # 预创建连接
        for _ in range(pool_size):
            self._pool.put(self._create_connection())

    def _create_connection(self):
        """创建新连接（线程安全）"""
        with self._lock:
            conn_id = self._created_count
            self._created_count += 1
        return {"id": conn_id, "created_at": time.time()}

    def get_connection(self, timeout: float = 5.0):
        """获取连接（阻塞直到有可用连接或超时）"""
        try:
            conn = self._pool.get(timeout=timeout)
            print(f"  [线程{threading.current_thread().name}] 获取连接 #{conn['id']}")
            return conn
        except:
            raise TimeoutError("连接池已满，获取连接超时")

    def release_connection(self, conn):
        """归还连接到池中"""
        print(f"  [线程{threading.current_thread().name}] 归还连接 #{conn['id']}")
        self._pool.put(conn)


# 模拟使用
pool = ConnectionPool(None, pool_size=3)

def worker(worker_id: int):
    try:
        conn = pool.get_connection()
        time.sleep(random.uniform(0.1, 0.5))  # 模拟使用连接
        pool.release_connection(conn)
    except TimeoutError as e:
        print(f"Worker {worker_id}: {e}")

# 5 个线程竞争 3 个连接
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,), name=f"W{i}")
    threads.append(t)
    t.start()
for t in threads:
    t.join()
```

---

## 13.4 异步编程（asyncio 入门）

**案例1：同步 vs 异步的直观对比**

```python
import asyncio
import time

# 同步版本：串行等待
def sync_tasks():
    print("任务1开始")
    time.sleep(1)      # 阻塞！什么都不能做
    print("任务1完成")
    print("任务2开始")
    time.sleep(1)
    print("任务2完成")
# 总耗时 2s

# 异步版本：并发等待
async def async_task(name, delay):
    print(f"{name}开始")
    await asyncio.sleep(delay)  # 非阻塞！让出控制权给其他协程
    print(f"{name}完成")

async def async_main():
    await asyncio.gather(
        async_task("任务1", 1),
        async_task("任务2", 1),
        async_task("任务3", 1),
    )
# 总耗时约 1s（三个任务并发执行）
```

**案例2：async/await 核心语法**

```python
import asyncio

# 定义协程函数
async def fetch_data(url: str) -> str:
    """模拟异步获取数据"""
    print(f"  开始获取: {url}")
    await asyncio.sleep(1)   # 模拟网络请求（非阻塞！）
    print(f"  完成获取: {url}")
    return f"数据来自 {url}"

# 运行协程
async def main():
    # 并发发起多个请求
    results = await asyncio.gather(
        fetch_data("https://api.example.com/users"),
        fetch_data("https://api.example.com/orders"),
        fetch_data("https://api.example.com/products"),
    )
    return results

# Python 3.7+ 推荐的运行方式
# results = asyncio.run(main())
# print(f"结果: {results}")
```

**案例3：工业级 —— 异步 HTTP 客户端（aiohttp 简化版）**

```python
import asyncio
import time
from typing import List, Dict

class AsyncAPIClient:
    """
    异步 API 客户端骨架。
    使用 asyncio + semaphore（信号量）控制并发数，
    避免同时发起过多请求触发限流。
    """

    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.results: Dict[str, object] = {}

    async def fetch_one(self, url: str) -> dict:
        """获取单个 URL（带并发控制）"""
        async with self.semaphore:  # 控制同时进行的请求数
            print(f"  ➤ 请求: {url}")
            # 实际: async with aiohttp.ClientSession() as session:
            #     async with session.get(url) as resp:
            #         return await resp.json()
            await asyncio.sleep(0.5)  # 模拟网络延迟
            print(f"  ✓ 完成: {url}")
            return {"url": url, "status": 200, "data": f"来自{url}的数据"}

    async def fetch_all(self, urls: List[str]) -> List[dict]:
        """并发获取所有 URL"""
        tasks = [self.fetch_one(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果，分离成功和失败
        successful = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                print(f"  ✗ 失败: {url} - {result}")
            else:
                successful.append(result)

        return successful


# 运行
async def run_demo():
    client = AsyncAPIClient(max_concurrent=3)
    urls = [f"https://api.example.com/items/{i}" for i in range(10)]
    start = time.perf_counter()
    results = await client.fetch_all(urls)
    elapsed = time.perf_counter() - start
    print(f"\n完成 {len(results)}/{len(urls)} 个请求，耗时 {elapsed:.2f}s")
    # 10个请求，3个并发 → 约 0.5×4=2s（而非 0.5×10=5s）

# asyncio.run(run_demo())
```

---

## 本章速查

| 场景 | 方案 | 关键类/函数 |
|------|------|------------|
| CPU 密集型并行 | 多进程 | `ProcessPoolExecutor` |
| I/O 密集型并发 | 多线程 | `ThreadPoolExecutor` |
| 高并发网络服务 | asyncio | `async/await`, `asyncio.gather()` |
| 线程安全 | Lock | `threading.Lock` |
| 线程安全队列 | Queue | `queue.Queue` |
| 并发数控制 | Semaphore | `asyncio.Semaphore` |

| 一句话 | 说明 |
|--------|------|
| GIL | CPython 的锁，同一时刻只有一个线程执行 Python 字节码 |
| 线程适合 I/O | I/O 操作会释放 GIL，所以多线程对 I/O 密集型有效 |
| 进程适合 CPU | 每个进程有独立 GIL，真正并行计算 |
| 协程不是线程 | 单线程内协作式多任务，await 处主动让出 |
