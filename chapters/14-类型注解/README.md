# 第十四章：类型注解与静态检查

---

## 理论：Python 是动态类型，为什么要加类型标注？

Python 运行时不管你是什么类型——你可以把 `int` 传给需要 `str` 的函数，但到运行时才发现 `TypeError`。**类型注解让你在写代码阶段就能发现这类错误**（借助 mypy 等工具）。

另外，类型注解本身就是**最好的文档**——看函数签名就知道参数和返回值是什么，不用读代码。

**核心理解**：类型注解不影响运行时行为。Python 解释器不检查它们。它们是给 IDE 和静态检查工具（mypy）看的。

---

### 关键字/语法

**基础类型**（Python 3.9+ 直接用小写）：

```python
def func(x: int, name: str, active: bool) -> float:
    pass

nums: list[int] = [1, 2, 3]
config: dict[str, str] = {"host": "localhost"}
point: tuple[float, float] = (3.0, 4.0)
ids: set[int] = {1, 2, 3}
```

**常用高级类型**：

```python
from typing import Optional, Union, Literal, Callable

# 可选（可能是 None）
def find(id: int) -> Optional[dict]:  # 等价 dict | None
    ...

# 联合（Python 3.10+ 推荐用 |）
value: int | str   # 等价 Union[int, str]

# 字面量——只能是这几个值
status: Literal["pending", "active", "done"]

# 可调用对象
handler: Callable[[int, str], bool]  # (int, str) → bool
```

---

### 案例

**案例1：函数类型注解——签名即文档**

```python
def create_user(
    name: str,
    age: int,
    email: str | None = None,  # Python 3.10+ 写法
) -> dict[str, object]:
    return {"name": name, "age": age, "email": email}

# 看签名就知道一切：
# - name 是 str（必填）
# - age 是 int（必填）
# - email 是 str 或 None（可选）
# - 返回 dict
```

**案例2：泛型——保持类型信息不丢失**

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """返回列表第一个元素，类型和列表元素类型一致"""
    return items[0] if items else None

num: int | None = first([1, 2, 3])    # T 推断为 int
text: str | None = first(["a", "b"])   # T 推断为 str
```

**案例3：TypedDict——给字典定义字段结构**

```python
from typing import TypedDict, Literal

class UserDict(TypedDict):
    id: int
    name: str
    role: Literal["admin", "user"]

def process(user: UserDict) -> str:
    return f"{user['name']} 是 {user['role']}"

# IDE 会提示 user 有哪些字段，mypy 会检查字段类型
```

---

## 本章速查

| 注解 | 含义 |
|------|------|
| `x: int` | 整数 |
| `x: str \| None` | 字符串或 None |
| `x: list[dict]` | dict 列表 |
| `Literal["a","b"]` | 只能是这几个字面量 |
| `Callable[[int], str]` | 函数：int → str |
| `T = TypeVar("T")` | 泛型变量 |
| `Protocol` | 静态鸭子类型 |
