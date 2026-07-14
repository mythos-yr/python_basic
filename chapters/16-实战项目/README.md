# 第十六章：实战项目路线图

> 学完所有基础知识后，最好的巩固方式就是做项目。以下是按难度递进的完整项目列表。

---

## 入门级项目（巩固语法）

### 项目1：命令行计算器

```python
"""
增强版命令行计算器。
覆盖知识点: 函数、异常处理、字典、循环、类型转换。
"""
from typing import Union

class Calculator:
    """支持四则运算 + 历史记录"""

    def __init__(self):
        self.history = []

    def calculate(self, expr: str) -> Union[float, str]:
        """解析并计算表达式，如 '3 + 5'"""
        try:
            parts = expr.strip().split()
            if len(parts) != 3:
                return "格式错误，请用: 数字 操作符 数字"

            a, op, b = float(parts[0]), parts[1], float(parts[2])

            operations = {
                "+": lambda x, y: x + y,
                "-": lambda x, y: x - y,
                "*": lambda x, y: x * y,
                "/": lambda x, y: x / y if y != 0 else "错误: 除数不能为零",
            }

            if op not in operations:
                return f"不支持的操作符: {op}"

            result = operations[op](a, b)
            self.history.append(f"{expr} = {result}")
            return result

        except ValueError:
            return "错误: 输入必须是数字"
        except Exception as e:
            return f"错误: {e}"

    def show_history(self, n: int = 10):
        print("\n=== 最近 {n} 条计算 ===")
        for h in self.history[-n:]:
            print(f"  {h}")


# 交互式运行
def main():
    calc = Calculator()
    print("命令行计算器 (输入 'quit' 退出, 'history' 查看历史)")
    while True:
        expr = input("> ").strip()
        if expr.lower() == "quit":
            break
        if expr.lower() == "history":
            calc.show_history()
            continue
        result = calc.calculate(expr)
        print(f"  = {result}")

if __name__ == "__main__":
    main()
```

**练习要点**：异常捕获、用户输入处理、无限循环 + break

---

### 项目2：密码生成器

```python
"""强密码生成器——覆盖: random、字符串操作、函数参数设计"""

import random
import string
import secrets  # 加密安全的随机数（生产环境用这个）

class PasswordGenerator:
    """灵活的密码生成器"""

    def __init__(self):
        self.lowercase = string.ascii_lowercase   # a-z
        self.uppercase = string.ascii_uppercase   # A-Z
        self.digits = string.digits               # 0-9
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate(
        self,
        length: int = 16,
        use_upper: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_similar: bool = True,  # 排除 1lI0O 等易混淆字符
    ) -> str:
        """生成密码"""
        char_pool = self.lowercase

        if use_upper:
            char_pool += self.uppercase
        if use_digits:
            char_pool += self.digits
        if use_symbols:
            char_pool += self.symbols

        if exclude_similar:
            for c in "1lI0Oo":
                char_pool = char_pool.replace(c, "")

        # secrets.choice 是加密安全的随机选择
        password = "".join(secrets.choice(char_pool) for _ in range(length))
        return password

    def generate_memorable(self, word_count: int = 4, separator: str = "-") -> str:
        """
        生成易记密码: 随机单词 + 数字 + 分隔符
        例: 'correct-horse-battery-staple-42'
        """
        common_words = [
            "apple", "bridge", "cloud", "dance", "eagle",
            "flame", "grape", "horse", "ivory", "jazz",
            "kite", "lemon", "moon", "noble", "ocean",
        ]
        words = [secrets.choice(common_words) for _ in range(word_count)]
        words.append(str(secrets.randbelow(100)))
        return separator.join(words)

    def evaluate_strength(self, password: str) -> str:
        """评估密码强度"""
        score = 0
        checks = [
            (len(password) >= 12, "长度≥12"),
            (len(password) >= 8, "长度≥8"),
            (any(c.islower() for c in password), "有小写"),
            (any(c.isupper() for c in password), "有大写"),
            (any(c.isdigit() for c in password), "有数字"),
            (any(c in self.symbols for c in password), "有符号"),
        ]
        passed = sum(1 for check, _ in checks if check)

        if passed >= 6:
            return "🟢 强"
        elif passed >= 4:
            return "🟡 中"
        else:
            return "🔴 弱"


gen = PasswordGenerator()
print(f"强密码: {gen.generate(20)}")
print(f"易记密码: {gen.generate_memorable()}")
print(f"强度: {gen.evaluate_strength('abc123')}")
print(f"强度: {gen.evaluate_strength(gen.generate(20))}")
```

---

## 进阶级项目（综合应用）

### 项目3：文件批量重命名工具

```python
"""
文件批量重命名工具。
覆盖: pathlib、正则表达式、CLI 参数、dry-run 模式、生成器。
"""
import re
import argparse
from pathlib import Path
from typing import Iterator, Tuple, Optional
from datetime import datetime

class BulkRenamer:
    """批量文件重命名器"""

    def __init__(self, directory: str, dry_run: bool = True):
        self.directory = Path(directory)
        self.dry_run = dry_run
        self.changes: list = []

    def find_files(self, pattern: str = "*") -> Iterator[Path]:
        """查找需要重命名的文件"""
        for f in self.directory.glob(pattern):
            if f.is_file():
                yield f

    def rename_with_pattern(
        self,
        old_pattern: str,
        new_pattern: str,
        file_pattern: str = "*",
    ) -> int:
        """
        正则替换重命名。
        例: old_pattern=r'IMG_(\d+)', new_pattern=r'photo_\1'
        """
        count = 0
        for filepath in self.find_files(file_pattern):
            new_name = re.sub(old_pattern, new_pattern, filepath.name)
            if new_name != filepath.name:
                new_path = filepath.parent / new_name
                self._apply_rename(filepath, new_path)
                count += 1
        return count

    def add_prefix_suffix(
        self,
        prefix: str = "",
        suffix: str = "",
        file_pattern: str = "*",
    ) -> int:
        """添加前缀和后缀"""
        count = 0
        for filepath in self.find_files(file_pattern):
            stem, ext = filepath.stem, filepath.suffix
            new_name = f"{prefix}{stem}{suffix}{ext}"
            new_path = filepath.parent / new_name
            self._apply_rename(filepath, new_path)
            count += 1
        return count

    def number_files(
        self,
        prefix: str = "file_",
        start: int = 1,
        padding: int = 3,
        file_pattern: str = "*",
    ) -> int:
        """按序号重命名"""
        count = 0
        for i, filepath in enumerate(self.find_files(file_pattern), start=start):
            ext = filepath.suffix
            new_name = f"{prefix}{i:0{padding}d}{ext}"
            new_path = filepath.parent / new_name
            self._apply_rename(filepath, new_path)
            count += 1
        return count

    def _apply_rename(self, old: Path, new: Path):
        """执行或模拟重命名"""
        self.changes.append((old.name, new.name))
        if not self.dry_run:
            old.rename(new)
        else:
            print(f"  [DRY RUN] {old.name} → {new.name}")

    def undo_last(self) -> int:
        """撤销上次的重命名"""
        count = 0
        for old_name, new_name in reversed(self.changes):
            old_path = self.directory / old_name
            new_path = self.directory / new_name
            if new_path.exists():
                new_path.rename(old_path)
                count += 1
        self.changes.clear()
        return count


# CLI 入口
def main():
    parser = argparse.ArgumentParser(description="批量文件重命名工具")
    parser.add_argument("directory", help="目标目录")
    parser.add_argument("--pattern", default="*", help="文件匹配模式")
    parser.add_argument("--prefix", help="添加前缀")
    parser.add_argument("--suffix", help="添加后缀")
    parser.add_argument("--regex-from", help="正则替换-查找模式")
    parser.add_argument("--regex-to", help="正则替换-替换为")
    parser.add_argument("--number", action="store_true", help="按序号重命名")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="预览模式（不实际修改文件）")
    parser.add_argument("--execute", action="store_true", help="实际执行（需谨慎）")

    args = parser.parse_args()

    renamer = BulkRenamer(args.directory, dry_run=not args.execute)

    if args.number:
        renamer.number_files(file_pattern=args.pattern)
    elif args.regex_from and args.regex_to:
        renamer.rename_with_pattern(args.regex_from, args.regex_to, args.pattern)
    elif args.prefix or args.suffix:
        renamer.add_prefix_suffix(args.prefix or "", args.suffix or "", args.pattern)

    print(f"\n共 {len(renamer.changes)} 个文件{'（预览模式，未实际修改）' if renamer.dry_run else '（已修改）'}")

if __name__ == "__main__":
    main()
```

---

### 项目4：简单的 REST API（FastAPI）

```python
"""
简易任务管理 API。
覆盖: FastAPI、Pydantic 模型、类型注解、CRUD 操作、异常处理。

安装依赖:
pip install fastapi uvicorn
"""

# 文件: main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import uuid4

# ===== 数据模型 =====
class TaskCreate(BaseModel):
    """创建任务的请求体"""
    title: str = Field(..., min_length=1, max_length=200, description="任务标题")
    description: Optional[str] = Field(None, max_length=2000)
    priority: int = Field(1, ge=1, le=5, description="优先级 1-5")

class TaskUpdate(BaseModel):
    """更新任务的请求体"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None

class Task(TaskCreate):
    """完整任务模型"""
    id: str
    created_at: datetime
    updated_at: datetime
    completed: bool = False

# ===== 内存存储 =====
tasks_db: dict[str, dict] = {}

# ===== FastAPI 应用 =====
app = FastAPI(title="任务管理 API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "任务管理 API", "docs": "/docs"}

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    """创建新任务"""
    task_id = str(uuid4())[:8]
    now = datetime.now()
    task_data = {
        "id": task_id,
        **task.model_dump(),
        "created_at": now,
        "updated_at": now,
        "completed": False,
    }
    tasks_db[task_id] = task_data
    return task_data

@app.get("/tasks", response_model=List[Task])
def list_tasks(
    completed: Optional[bool] = Query(None, description="按完成状态筛选"),
    priority: Optional[int] = Query(None, ge=1, le=5),
    limit: int = Query(50, le=100),
):
    """获取任务列表（支持筛选）"""
    result = list(tasks_db.values())

    if completed is not None:
        result = [t for t in result if t["completed"] == completed]
    if priority is not None:
        result = [t for t in result if t["priority"] == priority]

    return result[:limit]

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    """获取单个任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    return tasks_db[task_id]

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, update: TaskUpdate):
    """更新任务（部分更新）"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")

    task = tasks_db[task_id]
    update_data = update.model_dump(exclude_unset=True)  # 只更新传入的字段
    task.update(update_data)
    task["updated_at"] = datetime.now()
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    """删除任务"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="任务不存在")
    del tasks_db[task_id]


# 运行:
# uvicorn main:app --reload
# 浏览器打开: http://127.0.0.1:8000/docs
```

---

### 项目5：日志分析器

```python
"""
生产级日志分析工具。
覆盖: 生成器、正则表达式、Counter、datetime、pathlib。

分析目标:
- 按日志级别统计
- 按时间段统计
- 找出 Top N 错误信息
- 检测异常模式（短时间内大量错误）
"""
import re
import gzip
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Iterator, Dict, List, Optional, Tuple

class LogAnalyzer:
    """日志分析器"""

    # 常见日志格式的正则（如: 2024-01-15 10:30:45 ERROR ...）
    LOG_PATTERN = re.compile(
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"   # 时间戳
        r"\s+(\w+)"                                       # 级别
        r"\s+(.+)$"                                       # 消息
    )

    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.levels: Counter = Counter()
        self.hourly_counts: Dict[str, Counter] = defaultdict(Counter)
        self.error_messages: Counter = Counter()

    def _open_file(self) -> Iterator[str]:
        """打开文件（支持 .gz 压缩文件）"""
        if self.log_path.suffix == ".gz":
            with gzip.open(self.log_path, "rt", encoding="utf-8", errors="ignore") as f:
                yield from f
        else:
            with open(self.log_path, encoding="utf-8", errors="ignore") as f:
                yield from f

    def parse(self) -> "LogAnalyzer":
        """解析日志文件"""
        for line in self._open_file():
            match = self.LOG_PATTERN.match(line.strip())
            if not match:
                continue

            timestamp_str, level, message = match.groups()

            # 统计级别
            self.levels[level] += 1

            # 按小时统计
            try:
                ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                hour_key = ts.strftime("%Y-%m-%d %H:00")
                self.hourly_counts[hour_key][level] += 1
            except ValueError:
                pass

            # 统计错误信息
            if level in ("ERROR", "CRITICAL"):
                # 简化消息（去除非关键差异）
                simplified = re.sub(r"\d+|0x[0-9a-fA-F]+", "<N>", message)
                self.error_messages[simplified] += 1

        return self

    def generate_report(self) -> str:
        """生成分析报告"""
        lines = []
        lines.append(f"=== 日志分析报告: {self.log_path.name} ===")
        lines.append(f"分析时间: {datetime.now():%Y-%m-%d %H:%M:%S}\n")

        # 1. 级别统计
        lines.append("--- 级别分布 ---")
        total = sum(self.levels.values())
        for level, count in self.levels.most_common():
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * int(pct / 2)
            lines.append(f"  {level:>10}: {count:>6} ({pct:5.1f}%) {bar}")
        lines.append(f"  {'总计':>10}: {total:>6}\n")

        # 2. 错误高峰时段
        lines.append("--- 错误高峰时段 (Top 5) ---")
        error_hours = []
        for hour, counts in self.hourly_counts.items():
            err_count = counts.get("ERROR", 0) + counts.get("CRITICAL", 0)
            if err_count > 0:
                error_hours.append((hour, err_count))
        error_hours.sort(key=lambda x: x[1], reverse=True)
        for hour, count in error_hours[:5]:
            lines.append(f"  {hour}: {count} 个错误")

        # 3. Top 错误消息
        lines.append(f"\n--- Top 错误消息 ---")
        for msg, count in self.error_messages.most_common(10):
            lines.append(f"  [{count:>4}次] {msg[:100]}")

        return "\n".join(lines)

    def detect_anomalies(self, threshold: int = 10) -> List[str]:
        """
        检测异常：一小时内错误超过阈值。
        """
        alerts = []
        for hour, counts in self.hourly_counts.items():
            err_count = counts.get("ERROR", 0) + counts.get("CRITICAL", 0)
            if err_count >= threshold:
                alerts.append(f"⚠️ {hour}: {err_count} 个错误（阈值: {threshold}）")
        return alerts


# 使用
# analyzer = LogAnalyzer("/var/log/app.log")
# analyzer.parse()
# report = analyzer.generate_report()
# print(report)
# for alert in analyzer.detect_anomalies(threshold=20):
#     print(alert)
```

---

## 高级项目（架构设计）

### 项目6：简易 ORM 框架

```python
"""
从零实现一个简易 ORM（对象关系映射）。
覆盖: 元类、描述符、类装饰器、魔术方法。

这是理解 Django ORM / SQLAlchemy 底层原理的最佳练习。
"""
from typing import Dict, Any, List, Optional, Type

# ===== 字段定义 =====
class Field:
    """数据库字段基类"""
    def __init__(self, primary_key: bool = False, nullable: bool = True, default=None):
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.name = None  # 在 ModelMeta 中设置

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return obj._data.get(self.name, self.default)

    def __set__(self, obj, value):
        obj._data[self.name] = value

class IntegerField(Field):
    pass

class StringField(Field):
    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

class FloatField(Field):
    pass

class BooleanField(Field):
    pass

# ===== 元类 =====
class ModelMeta(type):
    """Model 的元类——自动收集字段定义"""

    def __new__(mcs, name, bases, namespace):
        if name == "Model":
            return super().__new__(mcs, name, bases, namespace)

        # 收集所有 Field 实例
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value

        cls = super().__new__(mcs, name, bases, namespace)
        cls._fields = fields

        # 确保有表名
        if not hasattr(cls, "__tablename__"):
            cls.__tablename__ = name.lower() + "s"

        return cls


# ===== 基类 =====
class Model(metaclass=ModelMeta):
    """所有模型的基类"""

    def __init__(self, **kwargs):
        self._data: Dict[str, Any] = {}

        # 设置字段默认值
        for field_name, field in self._fields.items():
            self._data[field_name] = field.default

        # 设置传入的值
        for key, value in kwargs.items():
            if key in self._fields:
                setattr(self, key, value)
            else:
                raise AttributeError(f"'{type(self).__name__}' 没有字段 '{key}'")

    def __repr__(self):
        fields = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{type(self).__name__}({fields})"

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)


# ===== 模拟数据库操作 =====
class QuerySet:
    """模拟查询集"""

    def __init__(self, model_class: Type[Model]):
        self.model_class = model_class
        self._filters: Dict[str, Any] = {}
        self._store = _global_store  # 模拟数据库

    def filter(self, **kwargs) -> "QuerySet":
        self._filters.update(kwargs)
        return self

    def all(self) -> List[Model]:
        table = self._store.get(self.model_class.__tablename__, [])
        result = []
        for data in table:
            match = all(data.get(k) == v for k, v in self._filters.items())
            if match:
                result.append(self.model_class(**data))
        return result

    def first(self) -> Optional[Model]:
        results = self.all()
        return results[0] if results else None

    def create(self, **kwargs) -> Model:
        instance = self.model_class(**kwargs)
        table = self._store.setdefault(self.model_class.__tablename__, [])
        table.append(instance.to_dict())
        return instance

    def delete(self) -> int:
        table = self._store.get(self.model_class.__tablename__, [])
        original_len = len(table)
        filtered = [
            d for d in table
            if not all(d.get(k) == v for k, v in self._filters.items())
        ]
        self._store[self.model_class.__tablename__] = filtered
        return original_len - len(filtered)


# 全局存储（模拟数据库）
_global_store: Dict[str, List[Dict]] = {}


# ===== 使用示例 =====
class User(Model):
    """用户模型"""
    __tablename__ = "users"

    id = IntegerField(primary_key=True)
    name = StringField(max_length=100)
    age = IntegerField(default=18)
    email = StringField(nullable=True)
    is_active = BooleanField(default=True)


class Post(Model):
    """文章模型"""
    __tablename__ = "posts"

    id = IntegerField(primary_key=True)
    title = StringField(max_length=200)
    content = StringField()
    author_id = IntegerField()


# CRUD 操作
user_manager = QuerySet(User)

# 创建
alice = user_manager.create(name="Alice", age=30, email="alice@example.com")
bob = user_manager.create(name="Bob", age=25)

print(f"创建: {alice}")
print(f"创建: {bob}")

# 查询
users = user_manager.all()
print(f"所有用户: {users}")

# 过滤
alice_found = user_manager.filter(name="Alice").first()
print(f"查找Alice: {alice_found}")

# 删除
deleted = user_manager.filter(age=25).delete()
print(f"删除了 {deleted} 个用户")

users_after = user_manager.all()
print(f"剩余用户: {users_after}")
```

---

## 项目难度对照

| 项目 | 难度 | 覆盖的核心知识点 |
|------|------|------------------|
| 命令行计算器 | ⭐ | 函数、异常处理、字典、循环 |
| 密码生成器 | ⭐ | random、字符串、参数设计 |
| 待办事项清单 | ⭐⭐ | 列表/字典 CRUD、文件持久化 |
| 文本统计器 | ⭐⭐ | 生成器、Counter、大文件处理 |
| 文件重命名工具 | ⭐⭐⭐ | pathlib、正则、CLI、dry-run |
| REST API | ⭐⭐⭐ | FastAPI、Pydantic、类型注解 |
| 日志分析器 | ⭐⭐⭐ | 生成器管道、re、Counter、异常检测 |
| Web 爬虫 | ⭐⭐⭐ | requests、BeautifulSoup、异步 |
| 简易 ORM | ⭐⭐⭐⭐ | 元类、描述符、魔术方法 |
| 聊天室 | ⭐⭐⭐⭐ | asyncio、WebSocket、并发 |
| 数据分析 | ⭐⭐⭐⭐ | pandas、matplotlib、numpy |

---

> **学习路线建议**：
> 1. 先完成两个 ⭐ 级项目，巩固基础语法（第1-4章）
> 2. 选一个 ⭐⭐ 级项目，练习函数和文件操作（第5-9章）
> 3. 完成一个 ⭐⭐⭐ 级项目，应用 OOP 和常用库（第10-11章）
> 4. 最后挑战 ⭐⭐⭐⭐ 级项目，理解底层机制（第12-13章）
