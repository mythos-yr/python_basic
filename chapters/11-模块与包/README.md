# 第十一章：模块与包

---

## 11.1 模块基础

### 知识点：import 的四种方式

**案例1：import 的不同写法及其影响**

```python
# 方式1: import module —— 导入整个模块，用 module.name 访问
import math
print(math.sqrt(16))           # 4.0
print(math.pi)                 # 3.14159...

# 方式2: from module import name —— 导入特定名称到当前命名空间
from math import sqrt, pi
print(sqrt(25))                # 5.0  —— 不需要 math. 前缀
print(pi)                      # 3.14159...

# 方式3: from module import * —— 导入所有公开名称（不推荐！）
# from math import *           # 污染命名空间，不知道什么被导入了

# 方式4: import module as alias —— 使用别名
import numpy as np             # 业界约定
import pandas as pd
arr = np.array([1, 2, 3])
```

**案例2：`__name__` 和 `"__main__"` —— 程序的入口**

```python
# 文件: my_module.py
def greet(name):
    return f"Hello, {name}!"

def add(a, b):
    return a + b

# 只在作为脚本直接运行时才执行
if __name__ == "__main__":
    # 这部分代码在被 import 时不会执行
    print("=== 模块自测 ===")
    print(greet("World"))
    print(add(3, 5))
    print("=== 测试通过 ===")
```

```python
# 文件: main.py
# import my_module 时，自测代码不会运行
# 但 greet 和 add 函数可以被使用
```

**案例3：工业级 —— 模块级别的配置与单例**

```python
# 文件: config.py
"""
应用配置模块。
模块本身是天然的单例——无论被 import 多少次，只加载一次。
"""
import os
from pathlib import Path

# 模块级别——只执行一次
print("加载配置模块...")

# 默认配置
_config = {
    "DEBUG": False,
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
    "REDIS_URL": "redis://localhost:6379",
}

# 从环境变量覆盖
for key in _config:
    env_value = os.getenv(f"APP_{key}")
    if env_value is not None:
        # 类型转换
        if isinstance(_config[key], bool):
            _config[key] = env_value.lower() in ("true", "1", "yes")
        elif isinstance(_config[key], int):
            _config[key] = int(env_value)
        else:
            _config[key] = env_value

def get(key, default=None):
    """获取配置值"""
    return _config.get(key, default)

def is_debug():
    return _config["DEBUG"]


# 在任何其他文件中：
# from config import get, is_debug
# config 模块只会加载一次，所有模块共享同一份配置
```

---

## 11.2 包管理

### 知识点：包的结构与 __init__.py

**案例1：包的导入方式**

```python
# 假设项目结构:
# mypackage/
#   __init__.py
#   core.py
#   utils.py
#   subpkg/
#     __init__.py
#     module.py

# __init__.py 的内容：
"""
from .core import CoreClass
from .utils import helper_function

__all__ = ["CoreClass", "helper_function"]
"""

# 使用方式：
# import mypackage                          # 导入包本身
# from mypackage import CoreClass           # 从 __init__.py 中导入
# from mypackage.core import CoreClass      # 从具体模块导入
# from mypackage.subpkg import module       # 从子包导入
```

**案例2：__all__ 控制 from xxx import * 的范围**

```python
# utils.py
__all__ = ["public_func", "CONSTANT"]  # 只导出这两个

CONSTANT = 42

def public_func():
    return "公开函数"

def _private_func():  # _ 开头 → 约定私有
    return "私有函数"

def hidden_func():    # 不在 __all__ 中
    return "被隐藏"


# 使用方:
# from utils import *
# public_func()   # ✅ 可用
# CONSTANT        # ✅ 可用
# hidden_func()   # ❌ NameError! —— 不在 __all__ 中
# _private_func() # ❌ NameError! —— _ 开头的也不会被导出
```

**案例3：工业级 —— 构建可发布的 Python 包**

```python
# 标准项目结构:
"""
my_project/
├── pyproject.toml       # 现代项目元数据（替代 setup.py）
├── README.md
├── LICENSE
├── src/
│   └── mypackage/       # 你的代码
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
└── docs/
    └── index.md
"""

# pyproject.toml 内容示例:
"""
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mypackage"
version = "0.1.0"
description = "My awesome package"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "MIT"}
authors = [{name = "Your Name", email = "you@example.com"}]

dependencies = [
    "requests>=2.28",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "black", "ruff", "mypy"]
test = ["pytest>=7.0", "pytest-cov"]

[project.scripts]
mycli = "mypackage.cli:main"

[tool.setuptools.packages.find]
where = ["src"]
"""

# 发布到 PyPI:
# pip install build twine
# python -m build
# twine upload dist/*
```

---

## 11.3 常用标准库速览

### 知识点：collections —— 高级容器

**案例1：deque、defaultdict、Counter 实战**

```python
from collections import deque, defaultdict, Counter

# deque: 双端队列，两端添加/删除都是 O(1)
# 经典场景：最近 N 条历史记录
history = deque(maxlen=5)          # 固定大小队列
for i in range(10):
    history.append(f"事件{i}")
print(list(history))                # 只保留最后5条: ['事件5', ..., '事件9']

# 从两端操作
dq = deque([1, 2, 3])
dq.appendleft(0)                    # [0, 1, 2, 3]
dq.pop()                            # [0, 1, 2]
dq.popleft()                        # [1, 2]

# defaultdict: 自动创建默认值
# 按首字母分组
words = ["apple", "banana", "avocado", "blueberry"]
groups = defaultdict(list)
for w in words:
    groups[w[0]].append(w)
print(dict(groups))  # {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry']}

# Counter: 频次统计
text = "abracadabra"
freq = Counter(text)
print(freq.most_common(3))  # [('a', 5), ('b', 2), ('r', 2)]
```

**案例2：functools —— 高阶函数工具**

```python
from functools import lru_cache, partial, reduce
import time

# lru_cache: 记忆化缓存（最实用的装饰器之一）
@lru_cache(maxsize=128)
def fibonacci(n):
    """缓存计算结果——同样的参数不重复计算"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

start = time.perf_counter()
print(f"fib(35) = {fibonacci(35)}")
print(f"耗时: {time.perf_counter() - start:.4f}s")  # 瞬间完成！

# partial: 固定函数的部分参数
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)   # 固定 exp=2
cube = partial(power, exp=3)     # 固定 exp=3
print(square(5))  # 25
print(cube(5))    # 125

# reduce: 累积归约
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)
print(f"乘积: {product}")  # 120
```

**案例3：工业级 —— 用 lru_cache 实现 API 响应缓存**

```python
import time
import hashlib
from functools import lru_cache, wraps
from typing import Dict, Any, Optional

class APICache:
    """
    API 响应缓存层。
    结合 lru_cache 和手动过期机制，减少对外部 API 的重复请求。
    """

    def __init__(self, maxsize: int = 256, ttl_seconds: float = 300):
        self.ttl = ttl_seconds
        self._timestamps: Dict[str, float] = {}

    def make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        raw = f"{args}:{sorted(kwargs.items())}"
        return hashlib.md5(raw.encode()).hexdigest()

    def cached(self, func):
        """缓存装饰器（lru_cache + TTL 过期）"""
        @lru_cache(maxsize=128)
        def _cached_func(cache_key: str):
            """lru_cache 只关心参数是否相同"""
            result = func()
            return result

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = self.make_key(*args, **kwargs)

            # 检查 TTL 是否过期
            now = time.time()
            if key in self._timestamps:
                if now - self._timestamps[key] < self.ttl:
                    return _cached_func(key)

            # 过期或首次访问：清除旧的缓存，重新计算
            _cached_func.cache_clear()
            result = _cached_func(key)
            self._timestamps[key] = now
            return result

        return wrapper


# 模拟昂贵的外部 API 调用
cache_manager = APICache(ttl_seconds=2)

@cache_manager.cached
def get_user_profile():
    """模拟调用外部 API 获取用户资料（昂贵操作）"""
    print("  [真实 API 调用]...")
    time.sleep(0.5)
    return {"name": "Alice", "last_updated": time.time()}

# 测试
for i in range(5):
    print(f"第{i+1}次调用: {get_user_profile()['last_updated']:.2f}")
    time.sleep(0.8)
# 前3次走缓存（相同时间戳），第4次 TTL 过期后刷新
```

---

### 知识点：datetime —— 日期时间处理

**案例1：datetime 的核心操作**

```python
from datetime import datetime, date, timedelta
import time

# 获取当前时间
now = datetime.now()
print(f"现在: {now}")

# 格式化输出
print(f"格式化: {now:%Y-%m-%d %H:%M:%S}")
print(f"ISO格式: {now.isoformat()}")

# 字符串解析
dt = datetime.strptime("2026-07-14 15:30:00", "%Y-%m-%d %H:%M:%S")
print(f"解析: {dt}")

# 时间计算（timedelta）
tomorrow = now + timedelta(days=1)
last_week = now - timedelta(weeks=1)
three_hours_later = now + timedelta(hours=3)

print(f"明天: {tomorrow:%Y-%m-%d}")
print(f"上周: {last_week:%Y-%m-%d}")

# 计算两个日期之间的天数
birthday = date(1995, 8, 15)
today = date.today()
days_alive = (today - birthday).days
print(f"活了 {days_alive:,} 天")
```

**案例2：时区处理（Python 3.9+）**

```python
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

# UTC 时间
utc_now = datetime.now(timezone.utc)
print(f"UTC: {utc_now}")

# 转换到不同时区
beijing_tz = ZoneInfo("Asia/Shanghai")
tokyo_tz = ZoneInfo("Asia/Tokyo")
ny_tz = ZoneInfo("America/New_York")

print(f"北京: {utc_now.astimezone(beijing_tz)}")
print(f"东京: {utc_now.astimezone(tokyo_tz)}")
print(f"纽约: {utc_now.astimezone(ny_tz)}")
```

**案例3：工业级 —— 时间窗口工具类**

```python
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

class TimeWindow:
    """
    时间窗口工具。
    用于生成报表时间范围、缓存过期、数据归档等场景。
    """

    @staticmethod
    def today_range(tz: Optional[str] = None) -> tuple:
        """今天 00:00:00 ~ 23:59:59"""
        tz_obj = ZoneInfo(tz) if tz else None
        now = datetime.now(tz_obj)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1) - timedelta(microseconds=1)
        return start, end

    @staticmethod
    def this_week_range() -> tuple:
        """本周一 00:00:00 ~ 本周日 23:59:59"""
        today = datetime.now()
        start = today - timedelta(days=today.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7) - timedelta(microseconds=1)
        return start, end

    @staticmethod
    def this_month_range() -> tuple:
        """本月1日 ~ 本月最后一日"""
        today = datetime.now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # 下月1号减1微秒 = 本月最后一刻
        if today.month == 12:
            next_month = today.replace(year=today.year+1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month+1, day=1)
        end = next_month - timedelta(microseconds=1)
        return start, end

    @staticmethod
    def format_for_sql(dt: datetime) -> str:
        """格式化为 SQL 兼容的时间字符串"""
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # 保留3位毫秒


# 生成报表查询的 SQL 时间参数
window = TimeWindow()
start, end = window.today_range("Asia/Shanghai")
print(f"今天: {TimeWindow.format_for_sql(start)} ~ {TimeWindow.format_for_sql(end)}")
```

---

## 本章速查

| 导入方式 | 使用场景 |
|----------|----------|
| `import module` | 使用整个模块，命名空间隔离好 |
| `from module import name` | 只使用特定函数/类 |
| `import module as alias` | 长名称或约定别名（np, pd） |
| `from .module import X` | 包内相对导入 |

| 标准库 | 一句话用途 |
|--------|-----------|
| `collections` | deque, defaultdict, Counter, OrderedDict |
| `functools` | lru_cache, partial, reduce, wraps |
| `datetime` | 日期时间处理 |
| `itertools` | 迭代器工具（count, cycle, chain, combinations） |
| `pathlib` | 现代文件路径操作 |
| `json` | JSON 序列化 |
| `re` | 正则表达式 |
