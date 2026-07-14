# 第十一章：模块与包

---

## 11.1 模块

### 理论：程序大了就要拆成多个文件

一个 `.py` 文件就是一个**模块**。通过 `import` 在其他地方使用它的内容。

**模块是天然的单例**：无论被 import 多少次，一个模块只被加载执行一次，结果缓存在 `sys.modules` 中。

---

### 关键字/语法

**import 的四种写法**：

| 写法 | 效果 | 使用方式 |
|------|------|---------|
| `import module` | 导入整个模块 | `module.func()` |
| `import module as alias` | 别名 | `alias.func()` |
| `from module import name` | 只导入特定名称 | 直接用 `func()` |
| `from module import *` | 导入所有公开名称 | 不推荐，污染命名空间 |

**关键变量**：

| 变量 | 作用 |
|------|------|
| `__name__` | 当前模块名；直接运行时为 `"__main__"` |
| `sys.path` | 模块搜索路径的列表 |
| `sys.modules` | 已加载模块的缓存字典 |
| `dir(module)` | 列出模块中所有名字 |

**`__name__ == "__main__"` 的作用**：当直接运行 `python module.py` 时，`__name__` 为 `"__main__"`；当被 `import module` 时，`__name__` 为 `"module"`。用于区分"独立运行"和"被导入"。

---

### 案例

**案例1：四种 import 方式的对比**

```python
# 1. 导入整个模块（命名空间隔离，推荐）
import math
print(math.sqrt(16))    # 4.0

# 2. 别名
import numpy as np
arr = np.array([1, 2, 3])

# 3. 只导入特定名称（方便，但要小心名字冲突）
from math import sqrt, pi
print(sqrt(25))          # 直接用，不需要 math. 前缀

# 4. 不推荐：from math import *  —— 你不知道导入了什么
```

**案例2：`__name__` 的经典用法——"既能导入，也能自测"**

```python
# my_module.py
def helper():
    return "工具函数"

if __name__ == "__main__":
    # 以下代码只在 python my_module.py 时运行
    # 被 import my_module 时不会运行
    print("=== 模块自测 ===")
    assert helper() == "工具函数"
    print("=== 通过 ===")
```

**案例3（工业级）：模块级配置单例**

```python
# config.py —— 利用"模块只加载一次"实现全局单例
import os

_config = {"DEBUG": False, "DB_HOST": "localhost", "DB_PORT": 5432}

# 启动时从环境变量覆盖
for key in _config:
    val = os.getenv(f"APP_{key}")
    if val is not None:
        _config[key] = type(_config[key])(val)

def get(key):       return _config.get(key)

# 任何文件中：from config import get; get("DB_HOST")
# 整个进程共享同一份配置
```

---

## 11.2 包

### 理论：把模块组织成目录树

**包 = 包含 `__init__.py` 的目录**。`__init__.py` 告诉 Python 此目录是包。Python 3.3+ 可以省略，但建议保留。

```python
mypkg/
├── __init__.py       # 让 mypkg 成为包
├── core.py
├── utils.py
└── subpkg/
    ├── __init__.py
    └── module.py
```

---

### 关键字/语法

**绝对导入 vs 相对导入**：

```python
# 绝对导入（写全路径）
from mypkg.core import CoreClass

# 相对导入（在包内部使用）
from .core import CoreClass    # . = 当前目录
from ..utils import helper     # .. = 上级目录
```

**`__all__`**：控制 `from module import *` 导出哪些名字：

```python
__all__ = ["public_func", "MyClass"]   # 只导出这两个
```

---

### 案例

**案例1：创建包和使用**

```python
# mypkg/__init__.py
from .core import CoreClass
from .utils import helper

__all__ = ["CoreClass", "helper"]

# 使用方:
# from mypkg import CoreClass, helper
```

**案例2：pyproject.toml 构建可发布包**

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[project.scripts]
mycli = "mypackage.cli:main"   # pip install 后可直接运行 mycli

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

---

## 11.3 常用标准库速查

### datetime——日期时间处理

```python
from datetime import datetime, timedelta, date

now = datetime.now()                              # 当前时间
print(now.strftime("%Y-%m-%d %H:%M:%S"))          # 格式化输出
dt = datetime.strptime("2026-07-14", "%Y-%m-%d")  # 字符串解析
tomorrow = now + timedelta(days=1)                # 时间计算

# 时间差
diff = datetime(2026, 7, 14) - datetime(2026, 7, 1)
print(diff.days)  # 13
```

### functools——高阶函数工具

```python
from functools import lru_cache, partial, reduce, wraps

# lru_cache: 缓存函数结果（最实用的装饰器之一）
@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)

# partial: 固定函数参数
square = partial(pow, exp=2)   # square(5) = 25

# reduce: 累积归约
from functools import reduce
product = reduce(lambda x, y: x * y, [1, 2, 3, 4, 5])  # 120
```

### collections——高级容器

```python
from collections import deque, defaultdict, Counter, namedtuple

# deque: 双端队列，两端 O(1)
dq = deque([1, 2, 3]); dq.appendleft(0); dq.pop()

# defaultdict: 自动创建默认值
dd = defaultdict(list)
for word in ["apple", "banana", "avocado"]:
    dd[word[0]].append(word)

# Counter: 频次统计
c = Counter("abracadabra")
print(c.most_common(2))  # [('a', 5), ('b', 2)]
```

### itertools——迭代器工具

```python
import itertools

itertools.count(start=0, step=2)      # 无限计数
itertools.cycle(["A", "B", "C"])      # 无限循环
itertools.chain([1,2], [3,4])         # 串联
itertools.combinations("ABC", 2)      # 组合
itertools.permutations("ABC", 2)      # 排列
itertools.product("AB", "12")         # 笛卡尔积
itertools.islice(it, 10)              # 取前 10 个
```

---

## 本章速查

| 导入方式 | 场景 |
|----------|------|
| `import module` | 用全部功能，命名空间隔离 |
| `from module import X` | 只用到几个名称 |
| `import numpy as np` | 长名模块用别名 |
| `from . import X` | 包内相对导入 |

| 标准库 | 一句话 |
|--------|--------|
| `collections` | deque, defaultdict, Counter, namedtuple |
| `functools` | lru_cache, partial, reduce, wraps |
| `datetime` | 时间日期 |
| `itertools` | count, cycle, chain, combinations, islice |
| `json` | JSON 序列化 |
| `pathlib` | 现代路径操作 |
