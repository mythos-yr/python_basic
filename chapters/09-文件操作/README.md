# 第九章：文件操作

---

## 9.1 文件读写

### 理论：open() 是 Python 和外部文件的桥梁

`open()` 返回一个**文件对象**，它是迭代器，可以逐行读取。用 `with` 保证使用完后自动关闭。

---

### 知识点：打开模式详解

| 模式 | 可读？ | 可写？ | 文件不存在 | 文件存在 | 用途 |
|------|--------|--------|-----------|---------|------|
| `r` | ✅ | ❌ | 报错 | 从头读 | 读取已有文件 |
| `w` | ❌ | ✅ | 创建 | **清空后重写** | 写新内容 |
| `a` | ❌ | ✅ | 创建 | **末尾追加** | 日志 |
| `x` | ❌ | ✅ | 创建 | **报错** | 防止覆盖 |
| `r+` | ✅ | ✅ | 报错 | 从头 | 读写已有文件 |

**附加修饰符**：

| 修饰符 | 含义 | 示例 |
|--------|------|------|
| `t` | 文本模式（默认），自动处理换行和编码 | `"rt"`, `"wt"` |
| `b` | 二进制模式，返回 `bytes` | `"rb"`, `"wb"`（图片、视频） |

**常用组合**：`"r"` = `"rt"`（文本读），`"rb"`（二进制读），`"w"`（文本写），`"a"`（追加）。

---

### 知识点：读文件的方式

| 方法 | 做什么 | 内存 | 适用 |
|------|--------|------|------|
| `f.read()` | 一次性读全部 | 全部文件大小 | 小文件 |
| `f.read(n)` | 读 n 个字符（或 n 字节） | n | 分块读 |
| `f.readline()` | 读一行（含 `\n`） | 一行 | 手动逐行 |
| `f.readlines()` | 读所有行，返回列表 | 全部 | 中等文件 |
| `for line in f` | **惰性逐行迭代** | 一行 | **大文件首选** |

**写文件**：

```python
f.write("字符串")        # 写字符串
f.writelines(["a\n","b\n"])  # 写多行（不会自动加换行！）
```

**文件指针**：

```python
f.tell()        # 当前指针位置
f.seek(0)       # 移到开头
f.seek(0, 2)    # 移到末尾（os.SEEK_END）
```

---

### 案例

**案例1：四种读文件方式的选择**

```python
# 1. read() —— 小文件（< 几 MB）
with open("file.txt", "r", encoding="utf-8") as f:
    all_text = f.read()

# 2. readline() —— 配合海象运算符逐行处理
with open("file.txt", "r", encoding="utf-8") as f:
    while (line := f.readline().strip()):
        print(line)

# 3. readlines() —— 中等文件
with open("file.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()   # 返回 list[str]

# 4. 直接迭代 —— 大文件（推荐！内存恒定）
with open("file.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
```

**案例2：w（覆盖）vs a（追加）的区别**

```python
# w 模式：每次打开都清空
with open("log.txt", "w") as f:
    f.write("第一行\n")
with open("log.txt", "w") as f:
    f.write("这也成了第一行\n")   # 之前的内容没了

# a 模式：每次在末尾加
with open("log.txt", "a") as f:
    f.write("追加的一行\n")       # 前面的内容保留
```

**案例3：rb/wb——二进制模式处理图片**

```python
# 复制图片：必须用二进制模式
with open("source.jpg", "rb") as src:
    with open("copy.jpg", "wb") as dst:
        while chunk := src.read(64 * 1024):  # 64KB 一块
            dst.write(chunk)
```

**案例4（工业级）：分块计算大文件 MD5**

```python
import hashlib

def file_md5(path: str) -> str:
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(64 * 1024):
            md5.update(chunk)
    return md5.hexdigest()
```

---

## 9.2 pathlib——现代路径操作

### 理论：pathlib 是 os.path 的面相对象替代

`pathlib.Path` 用 `/` 运算符合并路径。Python 3.6 后几乎所有接受字符串路径的函数也接受 Path 对象。

---

### 知识点：Path 常用属性和方法

```python
from pathlib import Path

p = Path("/usr/local/bin/python3")

# 属性和组成部分
p.name              # 'python3'    文件名
p.stem              # 'python3'    无后缀文件名
p.suffix            # ''           后缀
p.parent            # Path('/usr/local/bin')  父目录
p.parts             # ('/', 'usr', 'local', 'bin', 'python3')

# 路径操作
Path("a") / "b" / "c.txt"   # Path('a/b/c.txt')  ← / 运算符合并
p.resolve()                  # 绝对路径
p.relative_to("/usr")        # 相对路径

# 判断
p.exists()           # 是否存在
p.is_file()          # 是文件？
p.is_dir()           # 是目录？

# 读写（pathlib 自带，不需要 open！）
p.read_text(encoding="utf-8")     # 读全文
p.write_text("hello", encoding="utf-8")  # 写全文
p.read_bytes()                     # 读二进制
p.write_bytes(b"data")             # 写二进制

# 目录操作
Path("new_dir").mkdir(parents=True, exist_ok=True)  # 递归创建
Path("empty_dir").rmdir()          # 删空目录
p.unlink(missing_ok=True)          # 删文件（不存在不报错）

# 遍历
p.glob("*.py")                     # 匹配（不递归）
p.rglob("*.py")                    # 递归匹配
```

---

### 案例

**案例1：pathlib vs os.path 风格对比**

```python
# os.path（旧式，字符串操作）
import os
print(os.path.basename("/a/b/c.txt"))        # c.txt
print(os.path.join("dir", "sub", "f.txt"))   # dir/sub/f.txt

# pathlib（现代，面向对象）
from pathlib import Path
p = Path("/a/b/c.txt")
print(p.name)                                 # c.txt
print(Path("dir") / "sub" / "f.txt")          # dir/sub/f.txt
```

**案例2：遍历目录下所有 Python 文件**

```python
from pathlib import Path

# 当前目录（不含子目录）
for f in Path(".").glob("*.py"):
    print(f)

# 递归所有子目录
for f in Path(".").rglob("*.py"):
    print(f"  {f} ({f.stat().st_size} bytes)")
```

**案例3（工业级）：文件差异检测——比较两个目录**

```python
import hashlib
from pathlib import Path

def dir_hashes(path: str) -> dict:
    """返回 {相对路径: MD5}"""
    root = Path(path)
    result = {}
    for f in root.rglob("*"):
        if f.is_file():
            rel = str(f.relative_to(root))
            result[rel] = hashlib.md5(f.read_bytes()).hexdigest()
    return result

old = dir_hashes("/backup/v1")
new = dir_hashes("/backup/v2")
added = set(new) - set(old)       # 新增文件
deleted = set(old) - set(new)     # 删除文件
modified = {f for f in set(new) & set(old) if old[f] != new[f]}  # 修改
```

---

## 9.3 JSON 处理

### 知识点：json 模块的四个核心函数

| 函数 | 方向 | 说明 |
|------|------|------|
| `json.dumps(obj)` | Python → JSON 字符串 | 序列化到字符串 |
| `json.loads(s)` | JSON 字符串 → Python | 从字符串反序列化 |
| `json.dump(obj, f)` | Python → JSON 文件 | 序列化到文件 |
| `json.load(f)` | JSON 文件 → Python | 从文件反序列化 |

**记忆技巧**：带 `s` = string；不带 `s` = file。

**常用参数**：

```python
json.dumps(data, indent=2, ensure_ascii=False)
#               ↑ 缩进美化    ↑ 允许中文等非 ASCII 字符
```

**JSON ↔ Python 类型映射**：

| JSON | Python |
|------|--------|
| object | dict |
| array | list |
| string | str |
| number | int / float |
| true/false | True / False |
| null | None |

---

### 案例

**案例1：四个核心函数的使用**

```python
import json
data = {"name": "Alice", "age": 30}

s = json.dumps(data, indent=2, ensure_ascii=False)   # → str
parsed = json.loads(s)                                # → dict

with open("data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)  # → file

with open("data.json") as f:
    loaded = json.load(f)                             # ← file
```

**案例2：自定义 JSON 编码器——处理 datetime 和 Decimal**

```python
import json
from datetime import datetime
from decimal import Decimal

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

data = {"time": datetime.now(), "price": Decimal("19.99")}
print(json.dumps(data, cls=CustomEncoder))
```

**案例3（工业级）：环境变量覆盖 JSON 配置**

```python
import json, os

def load_config(path: str) -> dict:
    with open(path) as f:
        config = json.load(f)
    for key in list(config.keys()):
        env_val = os.getenv(f"APP_{key.upper()}")
        if env_val is not None:
            # 保持原配置值的类型
            config[key] = type(config[key])(env_val)
    return config

# config = load_config("config.json")
# 如果设置了 export APP_DB_HOST=prod.example.com
# 则 config["db_host"] 被覆盖为 "prod.example.com"
```

---

## 9.4 CSV 处理

### 知识点：csv 模块的核心类

| 类 | 做什么 |
|----|--------|
| `csv.reader(f)` | 逐行读 CSV，每行是 list |
| `csv.writer(f)` | 逐行写 CSV |
| `csv.DictReader(f)` | 逐行读 CSV，每行是 dict（键来自表头） |
| `csv.DictWriter(f, fieldnames=...)` | 逐行写 CSV，用 dict |

---

### 案例

```python
import csv

# 写 CSV
with open("users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerows([("Alice", 30), ("Bob", 25)])

# 读 CSV（列表模式）
with open("users.csv", encoding="utf-8") as f:
    for row in csv.reader(f):
        print(row)

# 读 CSV（字典模式——推荐，语义更清晰）
with open("users.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        print(f"{row['name']}, {row['age']}岁")

# 写 CSV（字典模式）
with open("out.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerows([{"name": "Alice", "age": 30}])
```

---

## 本章速查

| 操作 | 代码 |
|------|------|
| 读全文 | `Path("f.txt").read_text()` |
| 写全文 | `Path("f.txt").write_text("...")` |
| 大文件逐行 | `for line in open("f.txt"):` |
| 分块读二进制 | `while chunk := f.read(65536):` |
| JSON 读 | `json.load(open("f.json"))` |
| JSON 写 | `json.dump(data, open("f.json", "w"))` |
| CSV 读 | `csv.DictReader(open("f.csv"))` |
| 路径拼接 | `Path("a") / "b" / "c.txt"` |
| 递归遍历 | `Path(".").rglob("*.py")` |
