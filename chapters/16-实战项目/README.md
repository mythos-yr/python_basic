# 第十六章：实战项目路线图

> 学完全部基础知识后，最好的巩固方式就是动手做项目。以下是按难度递进的项目列表。

---

## 入门级（巩固语法）

### 项目1：命令行计算器 ⭐

**覆盖**：函数、异常处理、字典、循环、input()

```python
def calculate(expr: str) -> str:
    """支持四则运算的简易计算器"""
    try:
        parts = expr.strip().split()
        a, op, b = float(parts[0]), parts[1], float(parts[2])
        ops = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y if y != 0 else "除数不能为零",
        }
        return str(ops[op](a, b))
    except Exception as e:
        return f"错误: {e}"

# 交互式运行
while True:
    expr = input("> ")
    if expr == "quit": break
    print(f"  = {calculate(expr)}")
```

### 项目2：密码生成器 ⭐

**覆盖**：random、字符串操作、参数设计

```python
import secrets
import string

def generate_password(length=16, use_symbols=True):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += "!@#$%^&*()"
    return "".join(secrets.choice(chars) for _ in range(length))

print(generate_password(20))
```

---

## 进阶级（综合应用）

### 项目3：文件批量重命名 ⭐⭐

**覆盖**：pathlib、正则、CLI、类型注解

```python
import re
from pathlib import Path

def bulk_rename(directory, pattern, replacement, dry_run=True):
    """正则批量重命名文件"""
    path = Path(directory)
    for f in path.glob("*"):
        if f.is_file():
            new_name = re.sub(pattern, replacement, f.name)
            if new_name != f.name:
                print(f"  {'[预览]' if dry_run else ''} {f.name} → {new_name}")
                if not dry_run:
                    f.rename(f.parent / new_name)

# bulk_rename(".", r"IMG_(\d+)", r"photo_\1", dry_run=True)
```

### 项目4：REST API（FastAPI） ⭐⭐⭐

**覆盖**：FastAPI、Pydantic、类型注解、CRUD

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    title: str
    done: bool = False

tasks = []

@app.get("/tasks")
def list_tasks():
    return tasks

@app.post("/tasks")
def create_task(task: Task):
    tasks.append(task)
    return task

# 运行: uvicorn main:app --reload
# 文档: http://localhost:8000/docs
```

---

## 高级（架构设计）

### 项目5：简易 ORM ⭐⭐⭐⭐

**覆盖**：元类、描述符、魔术方法

```python
class Field:
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    def __get__(self, obj, owner=None):
        return getattr(obj, self.name, None) if obj else self
    def __set__(self, obj, value):
        setattr(obj, self.name, value)

class ModelMeta(type):
    def __new__(mcs, name, bases, ns):
        ns["_fields"] = {k: v for k, v in ns.items() if isinstance(v, Field)}
        return super().__new__(mcs, name, bases, ns)

class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for k in self._fields:
            setattr(self, k, kwargs.get(k))

class User(Model):
    name = Field()
    age = Field()

user = User(name="Alice", age=30)
print(user.name)  # Alice
```

---

## 项目难度对照

| 项目 | 难度 | 核心知识点 |
|------|------|-----------|
| 计算器 | ⭐ | 函数、异常、字典、循环 |
| 密码生成器 | ⭐ | random、字符串、参数设计 |
| 待办事项 | ⭐⭐ | 列表/字典 CRUD、文件持久化 |
| 文本统计器 | ⭐⭐ | 生成器、Counter、大文件处理 |
| 文件重命名 | ⭐⭐⭐ | pathlib、正则、CLI |
| REST API | ⭐⭐⭐ | FastAPI、Pydantic、类型注解 |
| 日志分析器 | ⭐⭐⭐ | 生成器管道、re、异常检测 |
| 简易 ORM | ⭐⭐⭐⭐ | 元类、描述符、魔术方法 |
| 聊天室 | ⭐⭐⭐⭐ | asyncio、WebSocket、并发 |

---

> **建议路线**：⭐ → ⭐⭐ → ⭐⭐⭐ → ⭐⭐⭐⭐，每做一个项目你就把对应的知识点真正"用"会了。
