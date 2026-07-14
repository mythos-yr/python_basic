# 第八章：异常处理与上下文管理器

---

## 8.1 异常基础

### 知识点：try/except/else/finally 四件套

**案例1：完整执行路径演示**

```python
def show_execution_flow(denominator):
    """演示 try/except/else/finally 每种情况的执行路径"""
    print(f"\n--- 调用: 10 / {denominator} ---")
    try:
        print("  1. try 块开始")
        result = 10 / denominator
        print(f"  2. try 块完成, result = {result}")
    except ZeroDivisionError:
        print("  3. except 块: 捕获 ZeroDivisionError")
    except Exception as e:
        print(f"  3. except 块: 捕获 {type(e).__name__}: {e}")
    else:
        print("  4. else 块: try 块没有发生异常")
    finally:
        print("  5. finally 块: 无论如何都会执行")

show_execution_flow(2)     # 正常: try → else → finally
show_execution_flow(0)     # 除零: try → except → finally
show_execution_flow("x")   # 类型错误: try → except(第二个) → finally
```

**案例2：finally 即使遇到 return 也会执行**

```python
def finally_with_return():
    """证明 finally 在任何情况下都会执行"""
    try:
        print("try 块")
        return "try 中的 return"
    except Exception:
        return "except 中的 return"
    finally:
        print("finally 块 —— 即使 try 中有 return，我也执行！")

result = finally_with_return()
print(f"返回值: {result}")
# 输出:
# try 块
# finally 块 —— 即使 try 中有 return，我也执行！
# 返回值: try 中的 return
```

**案例3：工业级 —— 资源安全的函数包装器**

```python
import logging
import traceback
from functools import wraps
from typing import Callable, Any, Type, Tuple

logger = logging.getLogger(__name__)

def safe_execute(
    default_return: Any = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_traceback: bool = True,
):
    """
    安全执行装饰器：捕获指定异常，记录日志，返回默认值。
    用于保护关键业务流程不因非致命错误而完全中断。
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.error(
                    f"[{func.__name__}] 执行失败: {type(e).__name__}: {e}"
                )
                if log_traceback:
                    logger.debug(traceback.format_exc())
                return default_return
        return wrapper
    return decorator


# 使用
@safe_execute(default_return=[], exceptions=(ConnectionError, TimeoutError))
def fetch_user_data(user_id: int):
    """从远程服务获取用户数据（可能网络异常）"""
    # response = requests.get(f"/api/users/{user_id}", timeout=5)
    # return response.json()
    raise ConnectionError("网络不可达")  # 模拟

result = fetch_user_data(123)
print(f"获取结果: {result}")  # []（默认值），程序没有崩溃
```

---

## 8.2 异常层级结构

**案例1：查看异常继承关系**

```python
# 异常层级（简化）
# BaseException
# ├── SystemExit
# ├── KeyboardInterrupt
# ├── GeneratorExit
# └── Exception
#     ├── ArithmeticError
#     │   ├── ZeroDivisionError
#     │   └── OverflowError
#     ├── LookupError
#     │   ├── IndexError
#     │   └── KeyError
#     ├── ValueError
#     ├── TypeError
#     ├── OSError
#     │   ├── FileNotFoundError
#     │   └── PermissionError
#     └── ...

# 打印异常的 MRO
print(ZeroDivisionError.__mro__)
# (<class 'ZeroDivisionError'>, <class 'ArithmeticError'>,
#  <class 'Exception'>, <class 'BaseException'>, <class 'object'>)

# 所以 except ArithmeticError 可以同时捕获 ZeroDivisionError 和 OverflowError
```

**案例2：捕获多个异常的正确姿势**

```python
# ✅ 正确：用元组捕获多种异常
def safe_int_convert(value):
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        # 同时捕获 ValueError（如 "abc"）和 TypeError（如 None）
        print(f"无法转换 '{value}': {type(e).__name__}: {e}")
        return 0

print(safe_int_convert("123"))    # 123
print(safe_int_convert("abc"))    # 0（捕获 ValueError）
print(safe_int_convert(None))     # 0（捕获 TypeError）

# ❌ 错误：先捕获宽泛的，再捕获具体的（永远不会执行）
# try:
#     ...
# except Exception:        # 先捕获了所有
#     ...
# except ValueError:       # 永远不会执行！
#     ...
```

**案例3：工业级 —— 分级异常处理策略**

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """自定义服务异常基类"""
    pass

class ValidationError(ServiceError):
    """参数校验失败 —— 客户端错误"""
    pass

class ResourceNotFoundError(ServiceError):
    """资源不存在 —— 客户端错误"""
    pass

class DatabaseError(ServiceError):
    """数据库错误 —— 服务端错误"""
    pass

class ExternalServiceError(ServiceError):
    """外部服务异常 —— 服务端错误（但非自身）"""
    pass


def process_request(action: str, data: dict) -> dict:
    """
    分级异常处理：
    - 客户端错误 → 返回 4xx
    - 服务端错误 → 返回 5xx
    - 未预期错误 → 500 + 隐藏内部细节
    """
    try:
        # 业务逻辑
        result = execute_business_logic(action, data)
        return {"code": 200, "data": result}

    except (ValidationError, ResourceNotFoundError) as e:
        # 客户端错误：返回明确的错误信息
        logger.warning(f"客户端错误: {e}")
        return {"code": 400, "error": str(e)}

    except DatabaseError as e:
        # 服务端数据库错误：记录详细日志，返回通用错误
        logger.error(f"数据库错误: {e}", exc_info=True)
        return {"code": 500, "error": "内部服务异常，请稍后重试"}

    except ExternalServiceError as e:
        # 外部服务错误：降级处理
        logger.error(f"下游服务异常: {e}")
        return {"code": 502, "error": "外部服务暂时不可用", "fallback": True}

    except Exception as e:
        # 未预期的错误：最外层兜底
        logger.critical(f"未预期错误: {e}", exc_info=True)
        return {"code": 500, "error": "系统内部错误"}


def execute_business_logic(action: str, data: dict):
    """模拟业务逻辑"""
    if not data.get("user_id"):
        raise ValidationError("缺少 user_id")
    if action == "get_user":
        return {"name": "Alice"}
    raise DatabaseError("连接池耗尽")
```

---

## 8.3 raise 与异常链

**案例1：raise 的三种用法**

```python
# 1. raise 具体异常
def validate_age(age):
    if age < 0 or age > 150:
        raise ValueError(f"年龄必须在 0-150 之间，得到: {age}")
    return age

# 2. raise 重新抛出当前异常（在 except 块中）
def process():
    try:
        1 / 0
    except ZeroDivisionError:
        print("记录日志后重新抛出...")
        raise   # 保留原始 traceback

# 3. raise from: 异常转换，保留因果链
def load_config(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError as e:
        raise RuntimeError(f"配置文件不存在: {path}") from e
```

**案例2：异常链——`raise from` vs 裸 `raise`**

```python
def demonstrate_exception_chain():
    """
    演示异常链：raise from 把底层异常的原因链接起来。
    """
    try:
        try:
            int("not_a_number")
        except ValueError as original:
            # raise from: 保留因果链
            raise TypeError("数值转换失败") from original
    except TypeError as e:
        print(f"异常: {e}")
        print(f"原因: {e.__cause__}")         # 原始的 ValueError
        print(f"上下文: {e.__context__}")      # 隐式链（如果不用 from，Python 也会自动设置）

demonstrate_exception_chain()
```

**案例3：工业级 —— 敏感信息清洗（防止异常泄露密码）**

```python
import re
from typing import Any, Dict

class SafeException(Exception):
    """安全异常：自动清洗敏感信息"""
    pass

class SensitiveDataSanitizer:
    """
    异常信息清洗器。
    在抛出异常前，从错误消息中移除密码、token 等敏感数据。
    """

    SENSITIVE_KEYS = {"password", "token", "secret", "api_key", "credit_card"}

    @classmethod
    def sanitize(cls, message: str) -> str:
        """清洗消息中的敏感信息"""
        # 替换 key=value 或 "key": "value" 中的敏感部分
        for key in cls.SENSITIVE_KEYS:
            pattern = rf'({key}[=:]\s*["\']?)([^"\'&,\s]+)'
            message = re.sub(pattern, r'\1***REDACTED***', message, flags=re.IGNORECASE)
        return message

    @classmethod
    def raise_safe(cls, exception_class, message: str, *args):
        """抛出清洗后的异常"""
        safe_msg = cls.sanitize(message)
        raise exception_class(safe_msg, *args)


# 使用
try:
    # 错误信息中包含敏感数据
    raw_msg = "连接失败: host=db.example.com, password=SuperSecret123, user=admin"
    SensitiveDataSanitizer.raise_safe(ConnectionError, raw_msg)
except ConnectionError as e:
    print(f"安全异常信息: {e}")
    # 连接失败: host=db.example.com, password=***REDACTED***, user=admin
```

---

## 8.4 上下文管理器

### 知识点：with 语句与 __enter__/__exit__

**案例1：with 语句的脱糖过程**

```python
# with open("file.txt") as f:
#     content = f.read()
#
# 等价于:

# f = open("file.txt")            # 1. 创建上下文管理器
# f = f.__enter__()               # 2. 调用 __enter__，返回值赋给 as 后的变量
# try:
#     content = f.read()           # 3. 执行 with 块
# except:
#     if not f.__exit__(*sys.exc_info()):  # 4. 异常时调用 __exit__
#         raise
# finally:
#     f.__exit__(None, None, None)  # 5. 无论如何都调用 __exit__
```

**案例2：自定义上下文管理器——数据库连接**

```python
class DatabaseConnection:
    """模拟数据库连接（演示 __enter__ 和 __exit__）"""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connected = False

    def __enter__(self):
        """进入上下文：建立连接"""
        print(f"🔌 连接数据库 {self.host}:{self.port}...")
        self.connected = True
        return self   # 返回的对象赋给 as 后的变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文：释放资源（一定执行）"""
        print(f"🔌 断开数据库连接")
        self.connected = False

        # 返回 True 表示异常已被处理（抑制异常）
        # 返回 False/None 表示异常继续传播
        if exc_type is not None:
            print(f"⚠️ 检测到异常: {exc_type.__name__}")
        return False   # 不抑制异常

    def execute(self, sql: str):
        if not self.connected:
            raise RuntimeError("未连接")
        print(f"  📝 执行: {sql}")
        return [{"id": 1, "name": "Alice"}]


# 正常使用
with DatabaseConnection("localhost", 5432) as db:
    db.execute("SELECT * FROM users")
# 🔌 连接数据库 localhost:5432...
#   📝 执行: SELECT * FROM users
# 🔌 断开数据库连接
```

**案例3：工业级 —— 计时代码块（性能剖析）**

```python
import time
from contextlib import contextmanager
from typing import Optional

class Timer:
    """
    计时器上下文管理器。
    自动记录代码块的执行时间，支持嵌套和命名。
    """

    _stack = []  # 嵌套计时器栈

    def __init__(self, name: str = "anonymous", silent: bool = False):
        self.name = name
        self.silent = silent
        self.start_time: float = 0
        self.elapsed: float = 0

    def __enter__(self):
        self._stack.append(self)
        self.start_time = time.perf_counter()

        indent = "  " * (len(self._stack) - 1)
        if not self.silent:
            print(f"{indent}⏱️ [{self.name}] 开始...")
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start_time
        self._stack.pop()

        indent = "  " * len(self._stack)
        if not self.silent:
            print(f"{indent}⏱️ [{self.name}] 完成，耗时: {self.elapsed:.4f}s")
        return False


# 使用（支持嵌套）
with Timer("总体流程"):
    # 模拟第一步
    with Timer("步骤1: 数据加载"):
        time.sleep(0.1)

    with Timer("步骤2: 数据计算"):
        # 嵌套的子步骤
        with Timer("步骤2.1: 矩阵运算"):
            time.sleep(0.05)
        with Timer("步骤2.2: 排序"):
            time.sleep(0.08)

    with Timer("步骤3: 结果输出"):
        time.sleep(0.06)

# 输出:
# ⏱️ [总体流程] 开始...
#   ⏱️ [步骤1: 数据加载] 开始...
#   ⏱️ [步骤1: 数据加载] 完成，耗时: 0.1002s
#   ⏱️ [步骤2: 数据计算] 开始...
#     ⏱️ [步骤2.1: 矩阵运算] 开始...
#     ⏱️ [步骤2.1: 矩阵运算] 完成，耗时: 0.0501s
#     ⏱️ [步骤2.2: 排序] 开始...
#     ⏱️ [步骤2.2: 排序] 完成，耗时: 0.0803s
#   ⏱️ [步骤2: 数据计算] 完成，耗时: 0.1309s
#   ⏱️ [步骤3: 结果输出] 开始...
#   ⏱️ [步骤3: 结果输出] 完成，耗时: 0.0602s
# ⏱️ [总体流程] 完成，耗时: 0.2918s
```

---

## 8.5 contextlib

**案例1：用 contextmanager 装饰器简化上下文管理器**

```python
from contextlib import contextmanager

# 用类写（繁琐）
class FileManagerClass:
    def __init__(self, path, mode):
        self.path = path
        self.mode = mode

    def __enter__(self):
        self.f = open(self.path, self.mode)
        return self.f

    def __exit__(self, *args):
        self.f.close()

# 用 @contextmanager 写（简洁）
@contextmanager
def file_manager(path, mode):
    """用生成器写上下文管理器——在 yield 处分开 enter 和 exit"""
    f = open(path, mode)
    try:
        yield f          # ← yield 之前 = __enter__
    finally:
        f.close()        # ← yield 之后 = __exit__(finally 保证一定执行)


# 使用方式完全相同
# with file_manager("test.txt", "w") as f:
#     f.write("hello")
```

**案例2：contextlib 常用工具**

```python
from contextlib import suppress, redirect_stdout, ExitStack
import io
import os

# suppress: 忽略指定异常（比 try/except pass 更简洁）
with suppress(FileNotFoundError):
    os.remove("nonexistent.txt")   # 文件不存在也不报错

# redirect_stdout: 重定向标准输出
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("这行输出被捕获了")
    print("这行也是")
output = buffer.getvalue()
print(f"捕获到的输出: {output.strip()}")
```

**案例3：工业级 —— ExitStack 管理多个动态资源**

```python
from contextlib import ExitStack
from typing import List

class ResourceManager:
    """
    动态资源管理器。场景：需要打开的文件/连接数量在运行时才确定。
    ExitStack 可以动态注册任意数量的上下文管理器，
    并保证它们按 LIFO 顺序正确关闭。
    """

    def __init__(self):
        self._stack = ExitStack()

    def open_all(self, filepaths: List[str]) -> List:
        """打开多个文件，全部失败或全部成功（原子性）"""
        files = []
        for path in filepaths:
            try:
                f = self._stack.enter_context(open(path))
                files.append(f)
            except Exception:
                # ExitStack 会自动关闭已经成功打开的文件
                print(f"打开 {path} 失败，回滚已打开的文件...")
                self.close_all()
                raise
        return files

    def close_all(self):
        """关闭所有资源（ExitStack 保证 LIFO 顺序）"""
        self._stack.close()


# 使用
manager = ResourceManager()
try:
    files = manager.open_all(["file1.txt", "file2.txt", "file3.txt"])
    for f in files:
        print(f"处理: {f.name}")
finally:
    manager.close_all()  # 所有文件都会被正确关闭
```

---

## 本章速查

| 关键字 | 作用 |
|--------|------|
| `try` | 包裹可能产生异常的代码 |
| `except X as e` | 捕获类型 X 的异常 |
| `else` | try 块无异常时执行 |
| `finally` | 无论如何都执行 |
| `raise` | 抛出异常（可带 from 建立因果链） |
| `with` | 上下文管理器，自动清理资源 |
| `__enter__` | with 开始时调用 |
| `__exit__` | with 结束时调用（接收 exc_type, exc_val, exc_tb） |

| 常见异常 | 触发条件 |
|----------|----------|
| `ValueError` | 类型正确但值不合法 |
| `TypeError` | 类型不匹配 |
| `KeyError` | 字典键不存在 |
| `IndexError` | 列表索引越界 |
| `FileNotFoundError` | 文件不存在 |
| `StopIteration` | 迭代器耗尽 |
