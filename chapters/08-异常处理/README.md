# 第八章：异常处理与上下文管理器

---

## 8.1 异常是什么

### 理论：程序出错不一定就要崩溃

异常（Exception）就是程序运行时遇到的"意外情况"。如果你不处理，程序就崩溃；如果你用 `try/except` 处理，程序可以优雅地应对。

**类比**：你打电话给客服。正常流程是"拨号→接通→交谈→挂断"。但如果占线（异常），你不会把手机砸了，而是稍后重拨（异常处理）。

Python 的异常分为层级结构：

```
BaseException          ← 所有异常的根
├── SystemExit           程序退出
├── KeyboardInterrupt    Ctrl+C
├── GeneratorExit        生成器关闭
└── Exception          ← 通常继承这个
    ├── ValueError       值不对
    ├── TypeError        类型不对
    ├── KeyError         字典键不存在
    ├── IndexError       列表索引越界
    ├── FileNotFoundError 文件不存在
    └── ...
```

---

### 关键字/语法

```python
try:
    # 可能出错的代码
except 异常类型 as e:
    # 出错时执行的代码
else:
    # try 没有出错时执行
finally:
    # 无论如何都执行（即使有 return）
```

| 关键字 | 作用 |
|--------|------|
| `try` | 包裹可能产生异常的代码 |
| `except X as e` | 捕获类型为 X 的异常，`e` 是异常对象 |
| `else` | try 无异常时才执行（放在 except 之后） |
| `finally` | 无论如何都执行，常用于释放资源 |
| `raise` | 主动抛出异常 |
| `raise from` | 抛出异常并保留因果链 |

**`else` 和 `finally` 的区别**：
- `else`：没出错才执行（业务逻辑的"成功路径"）
- `finally`：出没出错都执行（资源的"清理路径"）

---

### 案例

**案例1：完整的四件套执行路径**

```python
def demo(x):
    try:
        result = 10 / x
    except ZeroDivisionError:
        print("except: 除零错误")
    except TypeError:
        print("except: 类型错误")
    else:
        print(f"else: 没有异常，结果={result}")
    finally:
        print("finally: 无论如何都执行")

demo(2)  # → try → else → finally
demo(0)  # → try → except → finally
```

**案例2：finally 即使有 return 也会执行**

```python
def test():
    try:
        return "try 返回"
    finally:
        print("finally 执行了！")  # 在 return 之前执行

print(test())
# finally 执行了！
# try 返回
```

**案例3：raise from——异常转换保留根因**

```python
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        # 把底层错误包装成更语义化的业务异常
        raise RuntimeError(f"配置加载失败: {path}") from e

# 调用方可以同时看到 RuntimeError 和导致它的 FileNotFoundError
```

**案例4（工业级）：分级异常处理策略**

```python
def process_request(action, data):
    try:
        result = execute(action, data)
        return {"code": 200, "data": result}

    except ValueError as e:
        # 客户端输入问题 → 400
        return {"code": 400, "error": str(e)}

    except ConnectionError as e:
        # 外部服务问题 → 502
        return {"code": 502, "error": "外部服务异常"}

    except Exception as e:
        # 兜底：记录完整日志，对外返回通用错误
        logger.exception("未知错误")
        return {"code": 500, "error": "内部错误"}
```

---

## 8.2 上下文管理器 (with)

### 理论：让 Python 帮你记得"善后"

打开文件后要关闭，获取锁后要释放，连接数据库后要断开。这些"获取→使用→释放"的模式太常见了，Python 提供了 `with` 语句来保证"释放"这步一定会执行。

**类比**：酒店入住。你进房间（`__enter__`），住一晚，退房（`__exit__`）。不管你是正常离开还是被赶出去，都得退房。with 就是那个保证"退房"一定发生的机制。

---

### 关键字/语法

```python
with 上下文管理器 as 变量名:
    # 使用资源
# 离开 with 块时，自动调用 __exit__ 释放资源
```

**实现上下文管理器有两种方式**：

1. **写类**：实现 `__enter__` 和 `__exit__` 方法
2. **用装饰器**：`@contextlib.contextmanager` + 生成器函数

---

### 案例

**案例1：用类实现数据库连接管理器**

```python
class Database:
    def __enter__(self):
        print("连接数据库...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("断开连接")  # 一定会执行

    def query(self, sql):
        print(f"执行: {sql}")

with Database() as db:
    db.query("SELECT * FROM users")
# 连接数据库...
# 执行: SELECT * FROM users
# 断开连接
```

**案例2：用 @contextmanager 实现——更简洁**

```python
from contextlib import contextmanager

@contextmanager
def file_manager(path, mode):
    f = open(path, mode)
    try:
        yield f          # yield 之前 = __enter__
    finally:
        f.close()        # finally = __exit__（保证一定执行）

with file_manager("test.txt", "w") as f:
    f.write("hello")
# 文件自动关闭
```

**案例3（工业级）：计时器——衡量代码块执行时间**

```python
import time

class Timer:
    def __init__(self, name=""):
        self.name = name

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start
        print(f"[{self.name}] 耗时: {self.elapsed:.4f}s")

with Timer("数据加载"):
    time.sleep(0.3)   # 模拟
# [数据加载] 耗时: 0.3002s
```

---

## 本章速查

| 关键字 | 作用 |
|--------|------|
| `try/except` | 捕获并处理异常 |
| `else` | 无异常时执行 |
| `finally` | 无论有无异常都执行 |
| `raise` | 抛出异常 |
| `raise from` | 保留因果链的异常转换 |
| `with` | 上下文管理器，自动善后 |
| `__enter__` | 进入 with 时调用 |
| `__exit__` | 离开 with 时调用（即使异常也会调用） |

| 常见内置异常 | 触发条件 |
|-------------|----------|
| `ValueError` | 类型对但值不对 |
| `TypeError` | 类型不匹配 |
| `KeyError` | 字典键不存在 |
| `IndexError` | 列表索引越界 |
| `FileNotFoundError` | 文件不存在 |
| `StopIteration` | 迭代器耗尽 |
