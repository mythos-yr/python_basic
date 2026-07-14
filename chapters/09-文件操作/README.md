# 第九章：文件操作

---

## 9.1 文件读写基础

### 知识点：打开模式与编码

**案例1：各种打开模式的含义和差异**

```python
# 文件打开模式速查:
# r  - 只读（文件必须存在）
# w  - 只写（文件存在则清空，不存在则创建）
# a  - 追加（文件存在则在末尾追加，不存在则创建）
# x  - 排他创建（文件已存在则报错）
# b  - 二进制模式（配合 r/w/a）
# t  - 文本模式（默认）
# +  - 读写同时

# r vs w vs a 的演示
import os

# 准备测试文件
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n第二行\n")

# r: 只读（文件不存在报错）
with open("demo.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(f"r 模式读取: {repr(content)}")

# a: 追加（不清空原有内容）
with open("demo.txt", "a", encoding="utf-8") as f:
    f.write("第三行\n")
# 文件内容变为: 第一行\n第二行\n第三行\n

# x: 排他创建
try:
    with open("demo.txt", "x") as f:   # 文件已存在，报错
        f.write("...")
except FileExistsError as e:
    print(f"x 模式报错: {e}")

os.remove("demo.txt")
```

**案例2：读文件的多种方式**

```python
# 创建一个测试文件
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("line1\nline2\nline3\nline4\nline5\n")

# 方式1: read() —— 一次性读入整个文件（小心大文件！）
with open("sample.txt", "r", encoding="utf-8") as f:
    all_text = f.read()

# 方式2: readline() —— 逐行读取
with open("sample.txt", "r", encoding="utf-8") as f:
    first_line = f.readline().strip()
    second_line = f.readline().strip()
    print(f"第1行: {first_line}, 第2行: {second_line}")

# 方式3: readlines() —— 所有行读入列表（内存中）
with open("sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()   # ['line1\n', 'line2\n', ...]

# 方式4: 直接迭代文件对象（推荐——惰性逐行读取）
with open("sample.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # 每次只在内存中保持一行

import os; os.remove("sample.txt")
```

**案例3：工业级 —— 大文件的安全处理**

```python
import os
import hashlib
from typing import Iterator, Optional

class LargeFileProcessor:
    """
    大文件安全处理器。
    核心原则：永远不要一次读入整个大文件。
    """

    CHUNK_SIZE = 64 * 1024  # 64KB 一块

    @classmethod
    def safe_read_lines(cls, path: str, encoding: str = "utf-8") -> Iterator[str]:
        """
        安全逐行读取大文件。
        即使文件有几十 GB，内存使用也恒定。
        """
        with open(path, "r", encoding=encoding, errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    yield line.strip()
                except Exception as e:
                    print(f"警告: 第 {line_num} 行解析失败: {e}")

    @classmethod
    def compute_md5(cls, path: str) -> str:
        """
        分块计算大文件的 MD5。
        不管文件多大，每次只在内存中保持 64KB。
        """
        md5 = hashlib.md5()
        with open(path, "rb") as f:   # 二进制模式
            while chunk := f.read(cls.CHUNK_SIZE):
                md5.update(chunk)
        return md5.hexdigest()

    @classmethod
    def count_lines_fast(cls, path: str) -> int:
        """
        快速统计大文件行数（不解析内容）。
        利用文件对象的迭代器特性。
        """
        with open(path, "rb") as f:
            return sum(1 for _ in f)

    @classmethod
    def tail(cls, path: str, n: int = 10) -> str:
        """
        获取文件最后 N 行（类似 Unix tail）。
        从文件末尾反向读取，不加载整个文件。
        """
        with open(path, "rb") as f:
            # 从文件末尾向前搜索换行符
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            buffer_size = 8192
            lines_found = 0
            block_num = -1
            data_parts = []

            while lines_found <= n and file_size + block_num * buffer_size > 0:
                seek_pos = max(0, file_size + (block_num - 1) * buffer_size)
                read_size = min(buffer_size, file_size + block_num * buffer_size - seek_pos)
                f.seek(max(0, seek_pos))
                data = f.read(read_size or buffer_size)
                data_parts.insert(0, data)
                lines_found += data.count(b"\n")
                block_num -= 1

            all_data = b"".join(data_parts)
            lines = all_data.split(b"\n")
            return b"\n".join(lines[-n:]).decode("utf-8", errors="replace")
```

---

## 9.2 文件操作进阶

### 知识点：pathlib —— 现代路径操作

**案例1：pathlib vs os.path 对比**

```python
from pathlib import Path

# 创建路径对象
p = Path("/usr/local/bin/python3")

# os.path 风格（旧式，不推荐）
import os
print(os.path.basename("/usr/local/bin/python3"))  # python3
print(os.path.dirname("/usr/local/bin/python3"))   # /usr/local/bin
print(os.path.splitext("file.txt"))                # ('file', '.txt')
print(os.path.join("dir", "subdir", "file.txt"))   # dir/subdir/file.txt

# pathlib 风格（现代，推荐）
print(p.name)           # python3
print(p.parent)         # /usr/local/bin
print(p.suffix)         # （无后缀）
print(Path("dir") / "subdir" / "file.txt")  # dir/subdir/file.txt（/ 运算符合并路径）

# 路径是否存在
# Path("some_file.txt").exists()

# 遍历目录
# for py_file in Path(".").glob("*.py"):
#     print(py_file)

# 递归遍历
# for py_file in Path(".").rglob("*.py"):
#     print(py_file)
```

**案例2：pathlib 的文件操作**

```python
from pathlib import Path

# 读写文件（pathlib 自带方法）
p = Path("test_pathlib.txt")
p.write_text("Hello, pathlib!", encoding="utf-8")
content = p.read_text(encoding="utf-8")
print(content)  # Hello, pathlib!

# 二进制读写
# p.write_bytes(b"binary data")
# data = p.read_bytes()

# 文件信息
print(f"文件名: {p.name}")
print(f"后缀: {p.suffix}")
print(f"父目录: {p.parent}")
print(f"绝对路径: {p.resolve()}")
print(f"是文件: {p.is_file()}")
print(f"是目录: {p.is_dir()}")

# 创建和删除
p.unlink(missing_ok=True)  # 删除文件（不存在也不报错）

# 创建目录
new_dir = Path("test_dir/subdir")
new_dir.mkdir(parents=True, exist_ok=True)  # 递归创建，存在也不报错
new_dir.rmdir()  # 删除空目录
Path("test_dir").rmdir()
```

**案例3：工业级 —— 文件同步工具（差异检测）**

```python
import hashlib
from pathlib import Path
from typing import Dict, Set, Tuple

class FileSyncChecker:
    """
    文件差异检测器——比较两个目录的异同。
    基于文件内容的 MD5（而非修改时间），更可靠。
    """

    @staticmethod
    def hash_file(filepath: Path) -> str:
        """计算文件的 MD5 哈希"""
        md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                md5.update(chunk)
        return md5.hexdigest()

    @classmethod
    def scan_directory(cls, root: str) -> Dict[str, str]:
        """
        扫描目录下所有文件，返回 {相对路径: MD5哈希}。
        """
        root_path = Path(root)
        file_hashes = {}

        for filepath in root_path.rglob("*"):
            if filepath.is_file() and not filepath.name.startswith("."):
                relative = filepath.relative_to(root_path)
                file_hashes[str(relative)] = cls.hash_file(filepath)

        return file_hashes

    @classmethod
    def compare(cls, source: str, target: str) -> Dict[str, list]:
        """
        比较两个目录。
        返回: {"added": [...], "modified": [...], "deleted": [...], "unchanged": [...]}
        """
        source_files = cls.scan_directory(source)
        target_files = cls.scan_directory(target)

        source_keys = set(source_files.keys())
        target_keys = set(target_files.keys())

        result = {
            "added": [],       # 源有目标无 → 新增
            "deleted": [],     # 目标有源无 → 需删除
            "modified": [],    # 两边都有但 MD5 不同 → 修改
            "unchanged": [],   # MD5 相同 → 未变化
        }

        for path in source_keys - target_keys:
            result["added"].append(path)

        for path in target_keys - source_keys:
            result["deleted"].append(path)

        for path in source_keys & target_keys:
            if source_files[path] != target_files[path]:
                result["modified"].append(path)
            else:
                result["unchanged"].append(path)

        return result


# 使用
# checker = FileSyncChecker()
# diff = checker.compare("./dir_v1", "./dir_v2")
# for category, files in diff.items():
#     print(f"\n{category}: {len(files)} 个文件")
#     for f in files[:5]:
#         print(f"  {f}")
```

---

## 9.3 JSON 与 CSV

### 知识点：JSON 序列化

**案例1：json 的四个核心方法**

```python
import json

data = {
    "name": "Alice",
    "age": 30,
    "tags": ["python", "dev"],
    "metadata": {"role": "admin"}
}

# json.dumps: Python对象 → JSON字符串
json_str = json.dumps(data, indent=2, ensure_ascii=False)
print(f"dumps: {json_str}")

# json.loads: JSON字符串 → Python对象
parsed = json.loads(json_str)
print(f"loads: {parsed}")

# json.dump: Python对象 → 文件（直接写文件）
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# json.load: 文件 → Python对象
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
print(f"load: {loaded}")

import os; os.remove("data.json")
```

**案例2：JSON 高级——自定义序列化器**

```python
import json
from datetime import datetime, date
from decimal import Decimal

class EnhancedJSONEncoder(json.JSONEncoder):
    """处理 Python 特有的类型：datetime、Decimal 等"""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        # 让父类处理未知类型（抛 TypeError）
        return super().default(obj)


# 使用自定义编码器
data_with_special = {
    "created_at": datetime.now(),
    "price": Decimal("19.99"),
    "tags": {"python", "json"},
}

json_str = json.dumps(data_with_special, cls=EnhancedJSONEncoder, indent=2)
print(json_str)
```

**案例3：工业级 —— 配置文件管理（JSON + 环境变量覆盖）**

```python
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """
    配置管理器。加载 JSON 配置文件，允许环境变量覆盖。
    环境变量优先级 > JSON 配置 > 默认值。
    """

    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        if config_path and Path(config_path).exists():
            self.load_json(config_path)

    def load_json(self, path: str) -> "ConfigManager":
        """加载 JSON 配置文件"""
        with open(path, "r", encoding="utf-8") as f:
            self._config = json.load(f)
        return self

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置。优先级: 环境变量 > JSON > default。
        环境变量用前缀 APP_，如 APP_DB_HOST。
        """
        # 1. 先检查环境变量
        env_key = f"APP_{key.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return self._cast_type(env_value, default)

        # 2. 检查 JSON 配置（支持嵌套加点号访问）
        value = self._config
        for part in key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return default
        return value if value is not None else default

    @staticmethod
    def _cast_type(value: str, default: Any) -> Any:
        """将环境变量字符串转为合适的类型"""
        if isinstance(default, bool):
            return value.lower() in ("true", "1", "yes")
        if isinstance(default, int):
            return int(value)
        if isinstance(default, float):
            return float(value)
        if isinstance(default, list):
            return json.loads(value)  # JSON 数组格式
        return value


# 使用演示
# 假设 config.json 内容:
# {"db": {"host": "localhost", "port": 5432}, "debug": false}

# config = ConfigManager("config.json")
# db_host = config.get("db.host")              # 来自 JSON
# db_port = config.get("db.port", 5432)        # 来自 JSON
# debug = config.get("debug", False)           # 来自 JSON，false

# 如果设置了环境变量:
# export APP_DB_HOST=prod.example.com
# db_host = config.get("db.host")  # 现在返回 "prod.example.com"
```

---

## 9.4 CSV 处理

**案例1：CSV 读写基础**

```python
import csv
from pathlib import Path

# 写入 CSV
with open("users.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age", "city"])         # 写表头
    writer.writerow(["Alice", 30, "Beijing"])         # 写数据行
    writer.writerows([                                # 批量写入
        ["Bob", 25, "Shanghai"],
        ["Charlie", 35, "Shenzhen"],
    ])

# 读取 CSV
with open("users.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)

# DictReader/Writer: 用字典操作（更语义化）
with open("users.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']}, {row['age']}岁, 来自{row['city']}")

import os; os.remove("users.csv")
```

**案例2：CSV 的常见坑——字段中的逗号和换行**

```python
import csv
import io

# CSV 中的特殊值：字段含逗号、引号、换行
data = [
    {"name": "Smith, John", "note": 'He said "hello"'},            # 逗号和引号
    {"name": "Jane Doe", "note": "第一行\n第二行"},                 # 换行
    {"name": "Bob", "note": "simple,csv,values"},                  # 逗号
]

# DictWriter 自动处理转义
output = io.StringIO()
writer = csv.DictWriter(output, fieldnames=["name", "note"])
writer.writeheader()
writer.writerows(data)

print("CSV 输出:")
print(output.getvalue())
# 可以看到字段内的逗号和换行被自动加引号包围并转义
```

**案例3：工业级 —— 大数据 CSV 的流式处理**

```python
import csv
from typing import Iterator, Dict, List, Optional
from pathlib import Path

class CSVStreamProcessor:
    """
    流式 CSV 处理器。
    对大 CSV 文件（几个 GB）逐行处理，不加载全量到内存。
    """

    @staticmethod
    def stream_read(filepath: str, encoding: str = "utf-8") -> Iterator[Dict[str, str]]:
        """
        流式读取 CSV 文件，逐行产出字典。
        """
        with open(filepath, "r", encoding=encoding) as f:
            reader = csv.DictReader(f)

            # 校验表头
            if not reader.fieldnames:
                raise ValueError(f"CSV 文件 {filepath} 缺少表头")

            for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                try:
                    yield row
                except Exception as e:
                    print(f"警告: 第 {row_num} 行解析失败: {e}")

    @staticmethod
    def filter_and_transform(
        source: str,
        target: str,
        predicate,
        transformer=None,
        chunk_size: int = 10000,
    ) -> int:
        """
        流式过滤和转换，分批写入。
        返回处理的总行数。
        """
        count = 0
        buffer: List[Dict] = []

        with open(target, "w", encoding="utf-8", newline="") as out_f:
            writer = None  # 延迟初始化

            for row in CSVStreamProcessor.stream_read(source):
                if predicate(row):
                    if transformer:
                        row = transformer(row)

                    buffer.append(row)
                    count += 1

                    # 达到批次大小，批量写入
                    if len(buffer) >= chunk_size:
                        if writer is None:
                            writer = csv.DictWriter(out_f, fieldnames=buffer[0].keys())
                            writer.writeheader()
                        writer.writerows(buffer)
                        buffer.clear()

            # 写入剩余数据
            if buffer:
                if writer is None:
                    writer = csv.DictWriter(out_f, fieldnames=buffer[0].keys())
                    writer.writeheader()
                writer.writerows(buffer)

        return count


# 使用演示
# processor = CSVStreamProcessor()
# count = processor.filter_and_transform(
#     "huge_input.csv",
#     "filtered_output.csv",
#     predicate=lambda row: int(row.get("age", 0)) >= 18,
#     transformer=lambda row: {**row, "status": "valid"},
# )
# print(f"处理了 {count:,} 条记录")
```

---

## 本章速查

| 操作 | 代码 |
|------|------|
| 读整个文件 | `Path("f.txt").read_text()` |
| 写整个文件 | `Path("f.txt").write_text("...")` |
| 逐行读 | `for line in open("f.txt"):` |
| JSON 读 | `json.load(open("f.json"))` |
| JSON 写 | `json.dump(data, open("f.json","w"))` |
| CSV 读 | `csv.DictReader(open("f.csv"))` |
| CSV 写 | `csv.DictWriter(open("f.csv","w"))` |
| 遍历目录 | `Path("dir").rglob("*.py")` |
| 路径拼接 | `Path("dir") / "sub" / "file.txt"` |
