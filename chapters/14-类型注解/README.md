# 第十四章：类型注解与静态检查

---

## 理论：Python 是动态类型，为什么加类型标注？

Python 运行时不管你是什么类型——写错类型到运行才发现 TypeError。**类型注解让你在写代码阶段就能发现这类错误**（借助 mypy），而且类型注解本身就是最好的**文档**。

**核心理解**：类型注解**不影响运行时**。Python 解释器完全忽略它们。它们是给 IDE（自动补全、错误提示）和静态检查工具（mypy）看的。

---

## 知识点：所有类型注解语法

### 基础类型（Python 3.9+ 可直接用小写）

```python
x: int = 42                            # 整数
y: float = 3.14                        # 浮点
z: bool = True                         # 布尔
s: str = "hello"                       # 字符串
b: bytes = b"data"                     # 字节串
n: None = None                         # None

# 容器
nums: list[int] = [1, 2, 3]            # 整数列表
d: dict[str, int] = {"a": 1}           # 字符串→整数字典
t: tuple[int, str] = (1, "a")          # 固定长度元组
t2: tuple[int, ...] = (1, 2, 3)        # 可变长度元组
s: set[float] = {1.0, 2.0}             # 浮点集合
```

### 函数注解

```python
def add(a: int, b: int) -> int:         # 参数类型 + 返回值类型
    return a + b

def no_return() -> None:                # 不返回值的函数
    print("hello")
```

### 可选和联合类型

```python
from typing import Optional, Union

# Optional[X] = X | None
def find(id: int) -> Optional[dict]:    # 可能返回 None
    ...

# Union（Python 3.10+ 推荐用 |）
value: int | str                        # 等价于 Union[int, str]
result: int | float | None              # 多种可能
```

### 其他常用类型

```python
from typing import Literal, Callable, Any, TypeVar

# Literal: 只能是这些字面量
status: Literal["pending", "active", "done"]

# Callable: 描述可调用对象
handler: Callable[[int, str], bool]   # (int, str) → bool

# Any: 任意类型（关闭类型检查）
data: Any = get_dynamic_data()

# TypeVar: 泛型变量
T = TypeVar("T")
def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

### TypedDict——定义字典结构

```python
from typing import TypedDict

class User(TypedDict):
    id: int
    name: str
    role: Literal["admin", "user"]

def process(u: User) -> str:
    return f"{u['name']} is {u['role']}"   # IDE 会提示字段
```

### Protocol——静态鸭子类型

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Readable(Protocol):
    def read(self) -> str: ...

# 任何有 read() 方法的类都满足 Readable 协议
# 不需要显式继承！
```

### TYPE_CHECKING——避免循环导入

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User   # 只在 mypy 检查时导入，运行时不执行

def get_user() -> "User":      # 用字符串形式引用未导入的类型
    ...
```

---

## 案例

**案例1：函数签名即文档**

```python
def create_user(
    name: str,
    age: int,
    email: str | None = None,   # 可能是 None
    tags: list[str] = [],        # 默认空列表
) -> dict[str, object]:
    return {"name": name, "age": age, "email": email, "tags": tags}

# 看函数签名就知道所有参数类型和返回值，不需要额外文档
```

**案例2：泛型保持类型信息**

```python
T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

num: int | None = first([1, 2, 3])       # T 推断为 int
text: str | None = first(["a", "b"])      # T 推断为 str
# mypy 能正确推断每种情况下的返回值类型
```

**案例3：mypy 配置和使用**

```bash
pip install mypy
mypy script.py                 # 检查单个文件
mypy --strict src/             # 严格模式
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
```

---

## 本章速查

| 注解 | 含义 |
|------|------|
| `x: int` | 整数 |
| `x: str \| None` | 字符串或 None（Python 3.10+） |
| `x: Optional[str]` | 同上（旧式） |
| `x: list[dict]` | dict 列表 |
| `Literal["a","b"]` | 只能这几个值 |
| `Callable[[int], str]` | 函数：int → str |
| `TypeVar("T")` | 泛型变量 |
| `TypedDict` | 给字典定义字段 |
| `Protocol` | 静态鸭子类型 |
| `TYPE_CHECKING` | 只在类型检查时为 True |
