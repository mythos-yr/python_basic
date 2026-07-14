# 第九章：文件操作

---

## 9.1 文件读写基础

### 理论：Python 如何与外部文件交互

Python 通过 `open()` 函数打开文件，返回一个**文件对象**。文件对象是一个迭代器，可以逐行读取。

**打开模式理解**：第二个参数决定了"怎么用这个文件"。

| 模式 | 含义 | 能读？ | 能写？ | 文件不存在？ | 文件存在？ |
|------|------|--------|--------|-------------|-----------|
| `r` | 只读 | ✅ | ❌ | 报错 | 从开头读 |
| `w` | 只写 | ❌ | ✅ | 创建 | **清空并重写** |
| `a` | 追加 | ❌ | ✅ | 创建 | 从末尾追加 |
| `x` | 排他创建 | ❌ | ✅ | 创建 | **报错** |
| `r+` | 读写 | ✅ | ✅ | 报错 | 从开头 |

**`b` 和 `t`**：`b` = 二进制（如图片），`t` = 文本（默认，自动处理编码）。

**为什么用 `with`？** 保证文件无论是否出错都会被正确关闭，防止文件句柄泄漏。

---

### 关键字/语法

```python
with open("文件路径", "模式", encoding="utf-8") as f:
    content = f.read()                    # 读全部
    line = f.readline()                   # 读一行
    lines = f.readlines()                 # 读所有行（返回列表）
    for line in f:                        # 逐行迭代（推荐——省内存）
        pass
    f.write("字符串")                      # 写文本
```

---

### 案例

**案例1：四种读文件的方式对比**

```python
# read() —— 一次性全读（小文件用）
with open("file.txt", "r", encoding="utf-8") as f:
    all_text = f.read()

# readline() —— 逐行手动读
with open("file.txt", "r", encoding="utf-8") as f:
    while (line := f.readline()):
        print(line.strip())

# readlines() —— 所有行读进列表（中等文件用）
with open("file.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 直接迭代文件对象 —— 惰性逐行读（大文件首选）
with open("file.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

**案例2：追加写 vs 覆盖写**

```python
# w 模式：每次打开都清空文件
with open("log.txt", "w") as f:
    f.write("第一行\n")

with open("log.txt", "w") as f:
    f.write("这也成了第一行\n")   # 之前的内容被清空了

# a 模式：每次在末尾追加
with open("log.txt", "a") as f:
    f.write("追加的一行\n")       # 内容不会被覆盖
```

**案例3（工业级）：分块计算大文件的 MD5**

```python
import hashlib

def file_md5(path: str, chunk_size: int = 64 * 1024) -> str:
    """计算文件 MD5，每次只读 64KB——多大的文件都不怕"""
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()
```

---

## 9.2 pathlib —— 现代路径操作

### 理论：告别 os.path，拥抱 pathlib

`pathlib` 是 Python 3.4+ 引入的**面向对象的路径处理库**。相比字符串操作的 `os.path`，`pathlib.Path` 更直观、更不容易出错。

**`/` 运算符**：Path 对象可以用 `/` 拼接路径，这是 Python 唯一重载了 `/` 运算符的标准库。

---

### 关键字/语法

```python
from pathlib import Path

Path("dir") / "subdir" / "file.txt"   # 路径拼接

p = Path("some_file.txt")
p.exists()         # 是否存在
p.is_file()        # 是否是文件
p.is_dir()         # 是否是目录
p.name             # 文件名 (含后缀)
p.stem             # 文件名 (不含后缀)
p.suffix           # 后缀 (.txt, .py)
p.parent           # 父目录
p.read_text()      # 读文本
p.write_text("..") # 写文本
p.glob("*.py")     # 匹配文件（返回迭代器）
p.rglob("*.py")    # 递归匹配
p.mkdir(parents=True, exist_ok=True)  # 递归创建目录
```

---

### 案例

**案例1：pathlib vs os.path 对比**

```python
# os.path 风格（旧式）
import os
print(os.path.basename("/usr/local/bin/python3"))  # python3
print(os.path.join("dir", "subdir", "file.txt"))   # dir/subdir/file.txt

# pathlib 风格（推荐）
from pathlib import Path
p = Path("/usr/local/bin/python3")
print(p.name)                                        # python3
print(Path("dir") / "subdir" / "file.txt")           # dir/subdir/file.txt
```

**案例2：遍历目录下所有 .py 文件**

```python
from pathlib import Path

# 只当前目录
for f in Path(".").glob("*.py"):
    print(f)

# 递归遍历所有子目录
for f in Path(".").rglob("*.py"):
    print(f)
```

**案例3：文件差异检测——比较两个目录**

```python
import hashlib
from pathlib import Path

def dir_hash(directory: str) -> dict:
    """扫描目录，返回 {文件路径: MD5}"""
    result = {}
    for f in Path(directory).rglob("*"):
        if f.is_file():
            with open(f, "rb") as fh:
                result[str(f)] = hashlib.md5(fh.read()).hexdigest()
    return result

# 比较两个目录哪些文件变了
# old_files = dir_hash("/backup/v1")
# new_files = dir_hash("/backup/v2")
# for path in set(new_files) - set(old_files):
#     print(f"新增: {path}")
```

---

## 9.3 JSON 处理

### 理论：JSON 是数据交换的通用语言

JSON（JavaScript Object Notation）是前后端通信的标准格式。Python 的 `json` 模块提供 4 个核心函数：

| 函数 | 方向 | 输入 → 输出 |
|------|------|------------|
| `json.dumps(obj)` | Python → 字符串 | dict → str |
| `json.loads(s)` | 字符串 → Python | str → dict |
| `json.dump(obj, f)` | Python → 文件 | dict → file |
| `json.load(f)` | 文件 → Python | file → dict |

**记忆技巧**：带 `s` 的是字符串（string）操作，不带 `s` 的是文件操作。

---

### 案例

**案例1：四个核心方法**

```python
import json

data = {"name": "Alice", "age": 30}

# Python → JSON 字符串
s = json.dumps(data, indent=2, ensure_ascii=False)

# JSON 字符串 → Python
parsed = json.loads(s)

# Python → JSON 文件
with open("data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# JSON 文件 → Python
with open("data.json") as f:
    loaded = json.load(f)
```

**案例2：自定义 JSON 序列化器——处理 datetime**

```python
import json
from datetime import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)  # 未知类型交给父类抛异常

data = {"created_at": datetime.now()}
print(json.dumps(data, cls=CustomEncoder))
```

**案例3（工业级）：环境变量覆盖 JSON 配置**

```python
import json
import os

def load_config(path: str) -> dict:
    """加载 JSON 配置，允许环境变量覆盖"""
    with open(path) as f:
        config = json.load(f)

    # 遍历所有键，检查是否有对应的环境变量
    for key in list(config.keys()):
        env_val = os.getenv(f"APP_{key.upper()}")
        if env_val is not None:
            config[key] = type(config[key])(env_val)  # 保持原类型
    return config
```

---

## 本章速查

| 操作 | 代码 |
|------|------|
| 读全部文本 | `Path("f.txt").read_text()` |
| 写全部文本 | `Path("f.txt").write_text("...")` |
| 逐行读（大文件） | `for line in open("f.txt"):` |
| JSON → dict | `json.loads(s)` / `json.load(f)` |
| dict → JSON | `json.dumps(d)` / `json.dump(d, f)` |
| 路径拼接 | `Path("a") / "b" / "c.txt"` |
| 遍历目录 | `Path(".").rglob("*.py")` |
