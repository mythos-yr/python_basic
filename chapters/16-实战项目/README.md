# 第十六章：实战项目路线图

> 学完全部基础知识后，最好的巩固方式就是动手做项目。

---

## 入门级（巩固语法）

### 项目1：命令行计算器 ⭐

**覆盖**：函数、异常处理、字典、while、海象运算符

```python
def calc(expr: str) -> str:
    try:
        parts = expr.strip().split()
        a, op, b = float(parts[0]), parts[1], float(parts[2])
        ops = {"+": lambda x, y: x + y, "-": lambda x, y: x - y,
               "*": lambda x, y: x * y, "/": lambda x, y: x / y if y else "NaN"}
        return str(ops[op](a, b))
    except Exception as e:
        return f"错误: {e}"

while True:
    if (expr := input("> ")) == "quit": break
    print(f"  = {calc(expr)}")
```

### 项目2：密码生成器 ⭐

**覆盖**：secrets 模块、字符串操作、参数设计

```python
import secrets, string

def generate(length=16, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols: chars += "!@#$%^&*()"
    return "".join(secrets.choice(chars) for _ in range(length))

print(generate(20))
```

### 项目3：待办事项清单 ⭐⭐

**覆盖**：list/dict CRUD、文件持久化、JSON

```python
import json
from pathlib import Path

class TodoList:
    def __init__(self, path="todos.json"):
        self.path = Path(path)
        self.items = json.loads(self.path.read_text()) if self.path.exists() else []

    def add(self, task): self.items.append({"task": task, "done": False}); self.save()
    def done(self, idx): self.items[idx]["done"] = True; self.save()
    def list(self):
        for i, t in enumerate(self.items):
            print(f"{'✅' if t['done'] else '⬜'} {i}: {t['task']}")
    def save(self): self.path.write_text(json.dumps(self.items, indent=2))

# todos = TodoList()
# todos.add("学 Python"); todos.list(); todos.done(0)
```

---

## 进阶级（综合应用）

### 项目4：文件批量重命名 ⭐⭐⭐

**覆盖**：pathlib、正则、argparse、dry-run 模式

```python
import re, argparse
from pathlib import Path

def rename(directory, pattern, replacement, dry_run=True):
    for f in Path(directory).iterdir():
        if f.is_file():
            new = re.sub(pattern, replacement, f.name)
            if new != f.name:
                print(f"  {'[预览]' if dry_run else ''} {f.name} → {new}")
                if not dry_run: f.rename(f.parent / new)

# python rename.py . --pattern "IMG_(\d+)" --replace "photo_\1"
```

### 项目5：REST API——FastAPI ⭐⭐⭐

**覆盖**：FastAPI、Pydantic、类型注解、HTTP

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
tasks: list[dict] = []

class Task(BaseModel):
    title: str
    done: bool = False

@app.get("/tasks")
def list_tasks(): return tasks

@app.post("/tasks", status_code=201)
def create_task(task: Task):
    tasks.append(task.model_dump())
    return task
# 运行: uvicorn main:app --reload
# 文档: http://localhost:8000/docs
```

### 项目6：日志分析器 ⭐⭐⭐

**覆盖**：生成器、正则、Counter、datetime

```python
import re
from collections import Counter

def analyze_log(path: str) -> dict:
    pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)")
    levels = Counter()

    with open(path) as f:
        for line in f:
            if m := pattern.match(line):
                levels[m.group(2)] += 1

    return dict(levels)

# result = analyze_log("app.log")
# print(result)  # {'INFO': 1523, 'ERROR': 42, 'WARN': 89}
```

---

## 高级（架构设计）

### 项目7：简易 ORM ⭐⭐⭐⭐

**覆盖**：元类、描述符、魔术方法

```python
from typing import Any

class Field:
    def __set_name__(self, owner, name): self.name = f"_{name}"
    def __get__(self, obj, owner=None):
        return getattr(obj, self.name, None) if obj else self
    def __set__(self, obj, value): setattr(obj, self.name, value)

class StringField(Field): pass
class IntegerField(Field): pass

class ModelMeta(type):
    def __new__(mcs, name, bases, ns):
        ns["_fields"] = {k: v for k, v in ns.items() if isinstance(v, Field)}
        return super().__new__(mcs, name, bases, ns)

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for k in self._fields:
            setattr(self, k, kwargs.get(k))

class User(Model):
    name = StringField()
    age = IntegerField()

user = User(name="Alice", age=30)
print(user.name, user.age)
```

### 项目8：简易聊天室 ⭐⭐⭐⭐

**覆盖**：asyncio、WebSocket、并发处理

```python
# 核心骨架
import asyncio

class ChatRoom:
    def __init__(self):
        self.clients: dict[str, asyncio.Queue] = {}

    async def join(self, name: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.clients[name] = queue
        return queue

    async def broadcast(self, sender: str, message: str):
        for name, queue in self.clients.items():
            if name != sender:
                await queue.put(f"[{sender}]: {message}")
```

---

## 项目难度对照

| 项目 | 难度 | 核心知识点 |
|------|------|-----------|
| 计算器 | ⭐ | 函数、异常、字典、while |
| 密码生成器 | ⭐ | random、字符串 |
| 待办事项 | ⭐⭐ | CRUD、JSON、文件 |
| 文本统计器 | ⭐⭐ | 生成器、Counter |
| 文件重命名 | ⭐⭐⭐ | pathlib、正则、CLI |
| REST API | ⭐⭐⭐ | FastAPI、Pydantic |
| 日志分析器 | ⭐⭐⭐ | 生成器管道、re、Counter |
| 简易 ORM | ⭐⭐⭐⭐ | 元类、描述符、魔术方法 |
| 聊天室 | ⭐⭐⭐⭐ | asyncio、WebSocket |

> **路线**：⭐ → ⭐⭐ → ⭐⭐⭐ → ⭐⭐⭐⭐，每完成一个项目，对应的知识点就被真正"用"会了。
