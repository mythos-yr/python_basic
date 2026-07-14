# 第十四章：类型注解与静态检查

---

## 14.1 类型注解基础

### 知识点：函数和变量的类型注解

**案例1：基本类型注解**

```python
from typing import List, Dict, Tuple, Set, Optional, Union

# 变量注解（Python 3.6+）
name: str = "Alice"
age: int = 30
scores: List[int] = [85, 92, 78]
config: Dict[str, str] = {"host": "localhost"}
point: Tuple[float, float] = (3.0, 4.0)
unique_ids: Set[int] = {1, 2, 3}

# 函数注解
def greet(name: str, age: int) -> str:
    return f"Hello, {name}, you are {age} years old"

# 可选类型：可能为 None
def find_user(user_id: int) -> Optional[dict]:
    """返回 Optional[dict] = dict | None"""
    if user_id > 0:
        return {"id": user_id, "name": "Alice"}
    return None

# 联合类型：可能是多种类型之一（Python 3.10+）
def process(value: int | str) -> str:      # 等价于 Union[int, str]
    return str(value)

# Python 3.9+ 直接用内置类型
def process_items(items: list[int]) -> dict[str, int]:
    return {str(i): i for i in items}
```

**案例2：Callable 和 Any**

```python
from typing import Callable, Any

# Callable: 描述可调用对象（函数）
# Callable[[参数类型], 返回值类型]
def apply_operation(
    x: int,
    y: int,
    operation: Callable[[int, int], int],  # 接受两个 int，返回 int 的函数
) -> int:
    return operation(x, y)

def add(a: int, b: int) -> int:
    return a + b

def multiply(a: int, b: int) -> int:
    return a * b

print(apply_operation(3, 5, add))       # 8
print(apply_operation(3, 5, multiply))  # 15

# Any: 接受任意类型
def log(message: Any) -> None:
    """message 可以是任何类型"""
    print(f"[LOG] {message}")

log("hello")
log(42)
log([1, 2, 3])
```

**案例3：工业级 —— 用类型注解提高代码可维护性**

```python
from typing import TypedDict, Literal, Protocol, runtime_checkable
from dataclasses import dataclass

# TypedDict: 为字典定义结构（如 JSON API 响应）
class UserResponse(TypedDict):
    id: int
    name: str
    email: str
    role: Literal["admin", "user", "guest"]  # 只能是这三个值之一

# Literal: 限制值只能是特定字面量
def set_status(status: Literal["active", "inactive", "suspended"]) -> bool:
    valid_statuses = {"active", "inactive", "suspended"}
    return status in valid_statuses

set_status("active")      # ✅
# set_status("deleted")   # type-checker 会报错！


# Protocol: 结构化子类型（静态鸭子类型）
@runtime_checkable
class Readable(Protocol):
    def read(self) -> str:
        ...

def process_reader(source: Readable) -> str:
    """任何有 read() 方法的对象都可以传入"""
    return source.read()


class FileReader:
    def read(self) -> str:
        return "从文件读取的数据"

class APIClient:
    def read(self) -> str:
        return "从 API 获取的数据"

# 都不需要继承 Readable，只要有 read() 方法就行
print(process_reader(FileReader()))
print(process_reader(APIClient()))


# 泛型函数（用 TypeVar）
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    """返回列表的第一个元素，类型与元素类型一致"""
    return items[0] if items else None

num: int | None = first([1, 2, 3])        # 推断为 int
text: str | None = first(["a", "b"])       # 推断为 str
```

---

## 14.2 高级类型

**案例1：泛型类**

```python
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class Cache(Generic[K, V]):
    """泛型缓存类——类型参数化，保持类型安全"""

    def __init__(self):
        self._store: dict[K, V] = {}

    def get(self, key: K) -> V | None:
        return self._store.get(key)

    def set(self, key: K, value: V) -> None:
        self._store[key] = value

# 使用不同类型的缓存
str_cache: Cache[str, str] = Cache()          # 键是 str，值是 str
int_cache: Cache[int, list[str]] = Cache()    # 键是 int，值是 list[str]

str_cache.set("name", "Alice")
# str_cache.set(42, "Bob")         # mypy 会报错！键必须是 str
```

**案例2：重载与类型守卫**

```python
from typing import overload, Union

# @overload: 为同一个函数声明多种参数-返回值组合
@overload
def normalize(value: str) -> str: ...

@overload
def normalize(value: int) -> float: ...

@overload
def normalize(value: None) -> None: ...

def normalize(value: Union[str, int, None]) -> Union[str, float, None]:
    """不同类型的输入对应不同类型的输出"""
    if isinstance(value, str):
        return value.strip().lower()
    elif isinstance(value, int):
        return float(value) / 100
    return None

# mypy 会根据参数类型推断返回值类型
result1: str = normalize("  HELLO  ")  # ✅ mypy 知道返回 str
result2: float = normalize(50)          # ✅ mypy 知道返回 float
```

**案例3：工业级 —— FastAPI 风格的路由参数类型定义**

```python
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

# 这种类型注解风格在很多 Web 框架（FastAPI、SQLAlchemy 等）中都能见到

class OrderStatus(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

@dataclass
class OrderFilter:
    """订单查询过滤器——类型即文档"""
    status: Optional[OrderStatus] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    user_id: Optional[int] = None
    limit: int = 20
    offset: int = 0

@dataclass
class OrderResponse:
    """订单响应模型"""
    id: int
    user_id: int
    amount: float
    status: OrderStatus
    items: List[str]

# 函数签名本身就成了最好的文档
def query_orders(filters: OrderFilter) -> List[OrderResponse]:
    """
    查询订单。
    参数和返回值的类型一目了然，不需要额外文档。
    """
    # 实际查询逻辑...
    return [
        OrderResponse(
            id=1,
            user_id=101,
            amount=99.9,
            status=OrderStatus.PAID,
            items=["Python Book", "T-shirt"],
        )
    ]

# 使用
f = OrderFilter(status=OrderStatus.PAID, min_amount=50.0)
orders = query_orders(f)
print(f"找到 {len(orders)} 个订单")
```

---

## 14.3 mypy 实战

**案例1：用 mypy 检查代码**

```bash
# 安装 mypy
pip install mypy

# 检查单个文件
mypy script.py

# 检查整个项目
mypy src/

# 严格模式（推荐在新项目中使用）
mypy --strict src/

# 生成 HTML 报告
mypy --html-report ./mypy_report src/
```

**案例2：pyproject.toml 中配置 mypy**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# 忽略缺少类型注解的第三方库
[[tool.mypy.overrides]]
module = [
    "requests",
    "numpy",
]
ignore_missing_imports = true
```

**案例3：逐步为老项目添加类型注解**

```python
# 从老项目逐步迁移到类型注解的策略

# 第1步：开启 mypy 最宽松的模式
# mypy.ini: [mypy] check_untyped_defs = True

# 第2步：先给新代码加注解
def new_feature(user_id: int) -> dict[str, object]:
    return {"id": user_id, "created": True}

# 第3步：给核心 API 函数加注解（影响面最大的）
# def login(username: str, password: str) -> Optional[User]: ...

# 第4步：用 typing.TYPE_CHECKING 避免循环导入
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User    # 只在类型检查时导入，运行时不会循环导入

# 第5步：最终开启 strict 模式
# mypy --strict src/
```

---

## 本章速查

| 写法 | 含义 |
|------|------|
| `x: int = 5` | 变量注解 |
| `def f(x: int) -> str` | 函数注解 |
| `Optional[str]` 或 `str \| None` | 可能为 None |
| `Union[int, str]` 或 `int \| str` | 联合类型 |
| `List[int]` 或 `list[int]` (3.9+) | 整数列表 |
| `Dict[str, int]` 或 `dict[str, int]` | 字符串→整数字典 |
| `Callable[[int], str]` | 接受 int 返回 str 的函数 |
| `Literal["a", "b"]` | 只能是特定字面量 |
| `TypedDict` | 为字典定义结构 |
| `Protocol` | 静态鸭子类型 |
| `TypeVar` | 泛型变量 |
| `TYPE_CHECKING` | 只在类型检查时为 True |
