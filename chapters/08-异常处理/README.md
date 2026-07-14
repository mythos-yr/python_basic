# 第八章：异常处理与上下文管理器

---

## 8.1 异常是什么

### 理论：程序出错不一定就崩溃

异常（Exception）是程序运行时遇到的"意外情况"。你不处理 → 程序崩溃；用 `try/except` 处理 → 优雅应对。

**类比**：打电话给客服。正常流程"拨号→接通→交谈→挂断"。占线（异常）时你不会砸手机，而是稍后重拨（异常处理）。

---

### 异常层级结构

```
BaseException          ← 所有异常的根
├── SystemExit           sys.exit() 触发
├── KeyboardInterrupt   Ctrl+C
├── GeneratorExit       生成器关闭
└── Exception          ← 通常自定义异常继承这个
    ├── ValueError      类型对但值不对
    ├── TypeError       类型不匹配
    ├── KeyError        字典键不存在
    ├── IndexError      列表索引越界
    ├── FileNotFoundError 文件不存在
    ├── ZeroDivisionError 除零
    ├── AttributeError  属性不存在
    └── OSError         操作系统相关
```

**⚠️ 不要用 `except BaseException` —— 这会捕获 SystemExit 和 KeyboardInterrupt，导致程序无法正常退出。通常用 `except Exception`。**

---

### 关键字/语法

```python
try:
    # 可能出错的代码
except 异常类型 as e:
    # 出错时执行
except (类型A, 类型B):     # 一次捕获多种
    ...
else:
    # try 没有出错时执行
finally:
    # 无论如何都执行（即使 try 或 except 中有 return）
```

| 关键字 | 作用 |
|--------|------|
| `try` | 包裹可能产生异常的代码 |
| `except X as e` | 捕获类型 X 的异常 |
| `except (A, B)` | 捕获多种异常（元组） |
| `else` | 无异常时执行（写在所有 except 之后） |
| `finally` | 一定执行（用于释放资源） |
| `raise` | 抛出异常 |
| `raise from e` | 抛出异常并保留因果链（`__cause__`） |

**`else` vs `finally`**：`else` 只在成功时执行（业务成功路径），`finally` 成功失败都执行（资源清理路径）。

**自定义异常**：继承 `Exception`，通常定义一个空的类体即可。

---

### 案例

**案例1：完整的四件套执行路径**

```python
def demo(x):
    try:
        result = 10 / x
    except ZeroDivisionError:
        print("except: 除零错误")
    except (TypeError, ValueError):
        print("except: 类型或值错误")    # 一次捕获多种
    else:
        print(f"else: 无异常，结果={result}")
    finally:
        print("finally: 一定执行")

demo(2)  # try → else → finally
demo(0)  # try → except → finally
```

**案例2：finally 在 return 之前执行**

```python
def test():
    try:
        return "A"
    finally:
        print("finally!")     # return 之前执行

print(test())  # "finally!\nA"
```

**案例3：raise from——异常转换保留根因**

```python
def load(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f"配置加载失败: {path}") from e
    # 调用方看到 RuntimeError，e.__cause__ 是原始 FileNotFoundError
```

**案例4：自定义异常类**

```python
class InsufficientFundsError(Exception):
    """余额不足"""
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"余额 {balance}，需要 {amount}，差 {amount - balance}")

# raise InsufficientFundsError(100, 200)
```

**案例5（工业级）：分级异常处理——4xx vs 5xx**

```python
def handle_request(action, data):
    try:
        result = execute(action, data)
        return {"code": 200, "data": result}
    except (ValueError, KeyError) as e:
        # 客户端错误 → 400
        return {"code": 400, "error": str(e)}
    except ConnectionError as e:
        # 外部服务错误 → 502
        return {"code": 502, "error": "上游服务异常"}
    except Exception:
        # 兜底 → 500（记录完整日志，对外返回模糊信息）
        import logging
        logging.exception("未预期错误")
        return {"code": 500, "error": "内部错误"}
```

---

## 8.2 上下文管理器 (with)

### 理论：让 Python 帮你"善后"

文件打开后要关，锁获取后要释放，数据库连接后要断开。这种"获取→使用→释放"的模式，`with` 保证"释放"一定执行。

**类比**：酒店入住（`__enter__`）、住宿、退房（`__exit__`）。不管正常退房还是被赶出来，退房这步都会发生。

---

### 关键字/语法

```python
with 上下文管理器 as 变量:
    # 使用资源
# 出 with 块时自动调用 __exit__ 释放资源
```

**实现方式的两种方式**：

| 方式 | 做法 |
|------|------|
| 写类 | 实现 `__enter__` 和 `__exit__(self, exc_type, exc_val, exc_tb)` |
| 装饰器 | `@contextlib.contextmanager` + 生成器（yield 前=enter，yield 后=exit） |

**contextlib 常用工具**：

| 工具 | 作用 |
|------|------|
| `contextlib.suppress(Error)` | 忽略指定异常（代替 try/except pass） |
| `contextlib.redirect_stdout(f)` | 重定向标准输出 |
| `contextlib.ExitStack()` | 动态管理多个上下文管理器 |

---

### 案例

**案例1：两种实现方式对比**

```python
# 方式1：类
class Database:
    def __enter__(self):
        print("连接..."); return self
    def __exit__(self, *args):
        print("断开")  # 异常时也会执行

# 方式2：@contextmanager（更简洁）
from contextlib import contextmanager

@contextmanager
def file_manager(path, mode):
    f = open(path, mode)
    try:     yield f     # ← yield 前 = __enter__
    finally: f.close()   # ← yield 后 = __exit__
```

**案例2：suppress——忽略指定异常**

```python
from contextlib import suppress
import os

# ❌ try/except pass 太啰嗦
# try: os.remove("x.txt")
# except FileNotFoundError: pass

# ✅ suppress
with suppress(FileNotFoundError):
    os.remove("x.txt")   # 文件不存在也不报错
```

**案例3（工业级）：计时器上下文管理器**

```python
import time

class Timer:
    def __init__(self, name=""): self.name = name
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, *args):
        print(f"[{self.name}] {time.perf_counter() - self.start:.4f}s")

with Timer("数据加载"):
    time.sleep(0.3)
# [数据加载] 0.3002s
```

**案例4（工业级）：ExitStack——管理数量不定的资源**

```python
from contextlib import ExitStack

def open_many(filepaths):
    with ExitStack() as stack:
        files = []
        for p in filepaths:
            files.append(stack.enter_context(open(p)))  # 动态注册
        # 处理 files...
        # 出 with 时自动按 LIFO 顺序关闭所有文件
```

---

## 本章速查

| 关键字 | 作用 |
|--------|------|
| `try/except` / `else` / `finally` | 异常处理四件套 |
| `raise` / `raise from` | 抛出异常 / 保留因果链 |
| `with` | 上下文管理器，自动善后 |
| `@contextmanager` | 用生成器简化上下文管理器 |
| `suppress(Error)` | 忽略指定异常 |
| `ExitStack` | 动态管理多个上下文管理器 |

| 常见异常 | 触发 |
|---------|------|
| `ValueError` | 类型对值不对 |
| `KeyError` | 字典键不存在 |
| `IndexError` | 列表越界 |
| `FileNotFoundError` | 文件不存在 |
