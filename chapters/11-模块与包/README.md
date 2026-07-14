# 第十一章：模块与包

---

## 11.1 模块

### 理论：为什么需要拆成多个文件？

任何超过 200 行的程序都该拆分。把相关函数/类放在一个 `.py` 文件里，就是**模块**。通过 `import` 在其他地方使用。

**模块是天然的单例**：无论被 import 多少次，一个模块只被加载执行一次（结果缓存在 `sys.modules` 中）。

---

### 关键字/语法

```python
import module                # 导入整个模块
from module import name      # 只导入特定名称
from module import name as alias  # 用别名
import module as alias       # 模块别名
```

| 变量 | 作用 |
|------|------|
| `__name__` | 当前模块名；直接运行时为 `"__main__"` |
| `sys.path` | 模块搜索路径列表 |
| `sys.modules` | 已加载模块的缓存字典 |

---

### 案例

**案例1：`__name__ == "__main__"` 的作用**

```python
# utils.py
def helper():
    return "工具函数"

if __name__ == "__main__":
    # 这部分只在直接运行 python utils.py 时执行
    # 被 import utils 时不会执行
    print("这是模块自测代码")
```

**案例2：三种 import 方式的区别**

```python
# import module —— 用 module.name 访问，命名空间隔离好
import math
print(math.sqrt(16))

# from module import name —— 直接用 name，但可能和现有变量冲突
from math import sqrt
print(sqrt(25))

# import as alias —— 处理长名字或约定别名
import numpy as np
print(np.array([1, 2, 3]))
```

**案例3（工业级）：模块级配置——利用"只加载一次"实现全局单例**

```python
# config.py
import os

_config = {
    "DEBUG": False,
    "DB_HOST": "localhost",
    "DB_PORT": 5432,
}

# 启动时从环境变量覆盖
for key in _config:
    env_val = os.getenv(f"APP_{key}")
    if env_val is not None:
        _config[key] = type(_config[key])(env_val)

def get(key):
    return _config.get(key)
```

---

## 11.2 包

### 理论：把模块组织成层级结构

**包就是一个包含 `__init__.py` 的目录**。`__init__.py` 告诉 Python：这个目录是一个包。

```python
# 项目结构
mypkg/
├── __init__.py      # ← 这个文件让 mypkg 成为包
├── core.py
└── utils.py

# 调用方式
from mypkg import core
from mypkg.core import some_func
```

### 案例

**案例1：包的相对导入和绝对导入**

```python
# mypkg/core.py
from .utils import helper      # 相对导入（推荐在包内使用）
from mypkg.utils import helper  # 绝对导入（写全路径）
```

**案例2：`__all__` 控制 `from xxx import *` 导出什么**

```python
# mypkg/__init__.py
__all__ = ["public_func", "CoreClass"]  # 只有这两个被导出

from .core import CoreClass
from .utils import public_func, _private_func
```

**案例3：用 pyproject.toml 构建可发布的包**

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = ["requests>=2.28"]

[project.scripts]
mycli = "mypackage.cli:main"     # pip install 后可直接运行 mycli

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.backends._legacy:_Backend"
```

---

## 11.3 常用标准库速查

### datetime

```python
from datetime import datetime, timedelta

now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))    # 格式化输出
dt = datetime.strptime("2026-07-14", "%Y-%m-%d")  # 字符串解析
tomorrow = now + timedelta(days=1)           # 时间计算
```

### functools

```python
from functools import lru_cache, partial

# 缓存函数结果（最有用的装饰器之一）
@lru_cache(maxsize=128)
def fib(n):
    if n < 2: return n
    return fib(n-1) + fib(n-2)   # 不用 lru_cache 会重复计算

# 固定函数参数
square = partial(pow, exp=2)
print(square(5))  # 25
```

### collections

```python
from collections import deque, defaultdict, Counter

# 固定大小队列（自动丢弃旧的）
history = deque(maxlen=5)
for i in range(10):
    history.append(i)
print(list(history))  # [5, 6, 7, 8, 9]

# 自动创建默认值的字典
groups = defaultdict(list)
for word in ["apple", "banana", "avocado"]:
    groups[word[0]].append(word)

# 频次统计
text = "abracadabra"
print(Counter(text).most_common(2))  # [('a', 5), ('b', 2)]
```

---

## 本章速查

| 导入方式 | 场景 |
|----------|------|
| `import module` | 用全部功能，命名空间隔离好 |
| `from module import X` | 只用特定几个类/函数 |
| `import module as alias` | 长名模块用别名（`import numpy as np`） |
| `from . import X` | 包内相对导入 |

| 标准库 | 用途 |
|--------|------|
| `collections` | deque, defaultdict, Counter |
| `functools` | lru_cache, partial, wraps |
| `datetime` | 时间日期处理 |
| `itertools` | 迭代器工具 |
| `pathlib` | 现代文件路径 |
| `json` | JSON 序列化 |
