# 第五章：函数 —— 抽象的第一层

---

## 5.1 函数基础

### 知识点：参数传递 —— "传对象引用"

Python 的参数传递既不是传值，也不是传引用，而是**传对象引用**（Call by Sharing）。

**案例1：不可变对象作为参数**

```python
def modify_int(x):
    """尝试修改传入的整数——不会影响外部"""
    print(f"函数内: 修改前 x 的 id = {id(x)}")
    x = 999               # 这创建了一个新对象，x 重新绑定
    print(f"函数内: 修改后 x 的 id = {id(x)}, x = {x}")

num = 42
print(f"函数外: 调用前 num 的 id = {id(num)}, num = {num}")
modify_int(num)
print(f"函数外: 调用后 num 的 id = {id(num)}, num = {num}")
# num 没有变化 —— 因为 int 不可变，x = 999 只是让 x 指向了新对象
```

**案例2：可变对象作为参数**

```python
def modify_list(lst):
    """修改传入的列表——会影响外部！"""
    print(f"函数内: 修改前 lst 的 id = {id(lst)}")
    lst.append(4)          # 原地修改（没有改变 lst 的绑定）
    print(f"函数内: 修改后 lst 的 id = {id(lst)}, lst = {lst}")

my_list = [1, 2, 3]
print(f"函数外: 调用前 my_list 的 id = {id(my_list)}, my_list = {my_list}")
modify_list(my_list)
print(f"函数外: 调用后 my_list 的 id = {id(my_list)}, my_list = {my_list}")
# my_list 变了！因为 append 修改的是同一个对象
```

**案例3：工业级 —— 防御可变参数修改的两种策略**

```python
from copy import deepcopy
from typing import List, Dict, Optional

class DataProcessor:
    """
    数据处理服务。演示两种防御策略：
    1. 调用方传入前拷贝
    2. 被调方接收后立刻拷贝
    """

    @staticmethod
    def strategy_1_caller_copies(data: List[Dict]):
        """调用方负责拷贝"""
        for item in data:       # 不修改原数据
            item["processed"] = True
        return data

    @staticmethod
    def strategy_2_receiver_copies(data: List[Dict]):
        """被调方立刻深拷贝（推荐：职责内聚，不依赖调用方自觉）"""
        data = deepcopy(data)   # ← 第一行就拷贝，之后随意修改
        for item in data:
            item["processed"] = True
            item["timestamp"] = "2024-01-01"
        return data


# 演示
original_data = [{"id": 1}, {"id": 2}]

# 方式1：调用方拷贝
result1 = DataProcessor.strategy_1_caller_copies(deepcopy(original_data))
print(f"方式1后 original_data: {original_data}")  # 不变

# 方式2：被调方拷贝
result2 = DataProcessor.strategy_2_receiver_copies(original_data)
print(f"方式2后 original_data: {original_data}")  # 也不变
# 但如果忘记拷贝呢？
result3 = DataProcessor.strategy_1_caller_copies(original_data)
print(f"方式1（忘拷贝）后 original_data: {original_data}")  # 被改了！
```

---

## 5.2 参数传递

### 知识点：位置参数、关键字参数、默认参数

**案例1：默认参数的经典陷阱**

```python
# ❌ 陷阱：默认参数只在函数定义时求值一次
def add_to_list_bad(item, target=[]):
    target.append(item)
    return target

print(add_to_list_bad(1))  # [1]
print(add_to_list_bad(2))  # [1, 2]  ← 同一个列表！
print(add_to_list_bad(3))  # [1, 2, 3]

# ✅ 正确做法
def add_to_list_good(item, target=None):
    if target is None:
        target = []        # 每次调用时重新创建
    target.append(item)
    return target

print(add_to_list_good(1))  # [1]
print(add_to_list_good(2))  # [2]  ← 每次都是新列表
print(add_to_list_good(3))  # [3]
```

**案例2：*args 和 **kwargs 的完整用法**

```python
def universal_function(*args, **kwargs):
    """
    万能函数签名——接收任意参数。
    展示如何接收和使用 args 和 kwargs。
    """
    print(f"位置参数 args: {args}")       # 元组
    print(f"关键字参数 kwargs: {kwargs}")  # 字典
    print()

# 各种调用方式
universal_function(1, 2, 3)
# args: (1, 2, 3), kwargs: {}

universal_function(name="Alice", age=30)
# args: (), kwargs: {'name': 'Alice', 'age': 30}

universal_function(1, 2, name="Bob", city="北京")
# args: (1, 2), kwargs: {'name': 'Bob', 'city': '北京'}

# 解包调用
numbers = [1, 2, 3]
info = {"name": "Charlie", "age": 25}
universal_function(*numbers, **info)
# args: (1, 2, 3), kwargs: {'name': 'Charlie', 'age': 25}
```

**案例3：工业级 —— 装饰器工厂（带参数的装饰器）**

```python
import functools
import time
from typing import Callable, Any

# 不带参数的装饰器（两层嵌套）
def timer(func: Callable) -> Callable:
    """简单的计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 执行耗时: {elapsed:.4f}s")
        return result
    return wrapper

# 带参数的装饰器（三层嵌套）
def retry(max_attempts: int = 3, delay: float = 1.0):
    """带参数的重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        print(f"第{attempt}次失败: {e}，{delay}s后重试...")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


# 使用
@timer
@retry(max_attempts=3, delay=0.1)
def unstable_api():
    """模拟不稳定的 API 调用"""
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络波动")
    return "数据获取成功"

# for _ in range(5):
#     try:
#         print(unstable_api())
#     except ConnectionError:
#         print("最终失败")
```

---

### 知识点：参数顺序规则

**案例1：参数定义的完整语法**

```python
# Python 3.8+ 参数定义的全部规则
def complex_function(
    pos_only,                # 仅限位置（在 / 之前）
    /,                       # ← / 分隔符：前面的参数只能按位置传
    pos_or_kw,               # 位置或关键字
    *,                       # ← * 分隔符：后面的参数只能按关键字传
    kw_only,                 # 仅限关键字
    **kwargs,                # 剩余关键字参数
):
    """完整的参数定义语法"""
    pass

# 调用时:
# complex_function(1, 2, kw_only=3)          # ✅
# complex_function(1, pos_or_kw=2, kw_only=3) # ✅
# complex_function(pos_only=1, ...)            # ❌ pos_only 不能按关键字传
# complex_function(1, 2, 3)                   # ❌ kw_only 必须用关键字
```

**案例2：keyword-only 参数的典型场景**

```python
# keyword-only 让函数更可读
def create_user(name, *, age, email=None, phone=None):
    """
    name: 位置参数（必须的，显然是什么）
    age, email, phone: keyword-only（避免调用时混淆）
    """
    user = {"name": name, "age": age}
    if email:
        user["email"] = email
    if phone:
        user["phone"] = phone
    return user

# ✅ 清晰可读
user = create_user("Alice", age=30, email="alice@example.com")
# ❌ 如果不强制 keyword-only，可能写出 create_user("Alice", 30, "alice@example.com")
#    哪个是 age，哪个是 email？不直观
```

**案例3：工业级 —— API 客户端的参数设计**

```python
from typing import Optional, Dict, Any
import requests

class APIClient:
    """
    展示工业级函数参数设计的最佳实践。
    1. 必选参数按位置传
    2. 可选参数用 keyword-only
    3. 配置类参数用 **kwargs 转发
    """

    def __init__(self, base_url: str, *, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(
        self,
        method: str,               # 必选，位置参数
        endpoint: str,              # 必选，位置参数
        *,                          # 以下都是 keyword-only
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        timeout: Optional[int] = None,   # 允许单次覆盖默认超时
        retry_count: int = 0,
        **extra_options,            # 转发给 requests 库的其他选项
    ) -> Dict[str, Any]:
        """
        发起 HTTP 请求。

        必选参数用位置传参保证调用简洁。
        可选参数用 keyword-only 避免混淆。
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        req_timeout = timeout or self.timeout

        for attempt in range(retry_count + 1):
            try:
                resp = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                    timeout=req_timeout,
                    **extra_options,  # 透传额外选项
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                if attempt >= retry_count:
                    raise
                print(f"请求失败，重试 {attempt + 1}/{retry_count}...")

        return {}  # unreachable


# 使用对比
client = APIClient("https://api.example.com", timeout=15)

# ✅ 清晰的调用
# data = client.request(
#     "GET", "/users/123",
#     headers={"Authorization": "Bearer xxx"},
#     retry_count=2,
# )

# 如果不用 keyword-only 会怎样？
# client.request("GET", "/users/123", {"page": 1}, None, {"Authorization": "..."}, None, 2)
# 👆 完全看不懂每个参数是什么意思！
```

---

## 5.3 作用域与闭包

### 知识点：LEGB 规则

**案例1：LEGB 查找顺序演示**

```python
# LEGB: Local → Enclosing → Global → Built-in

x = "global"                  # Global

def outer():
    x = "enclosing"           # Enclosing (对于 inner 来说)

    def inner():
        x = "local"           # Local
        print(f"inner 中的 x: {x}")   # local（优先找到 Local）

    inner()
    print(f"outer 中的 x: {x}")       # enclosing

outer()
print(f"全局的 x: {x}")              # global

# 删除 inner 中的 x，看查找链的变化
def outer2():
    x = "enclosing"

    def inner2():
        # x 不存在于 local → 找 enclosing
        print(f"inner2 中的 x: {x}")

    inner2()

outer2()
```

**案例2：global 和 nonlocal 的使用**

```python
# global: 声明使用的是全局变量
count = 0

def increment_global():
    global count            # 没有这行，"count += 1"会报 UnboundLocalError
    count += 1

increment_global()
print(count)  # 1

# nonlocal: 声明使用的是外层函数的变量
def make_counter():
    count = 0               # enclosing 作用域

    def increment():
        nonlocal count       # 没有这行，"count += 1"会报错
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

**案例3：工业级 —— 闭包实现策略模式**

```python
from typing import Callable, Dict

def make_tax_calculator(country: str) -> Callable[[float], float]:
    """
    用闭包创建不同国家的税率计算器。
    每个计算器"自带"对应国家的税率信息——这就是闭包的价值。
    """

    # 税率表（封闭在闭包中）
    tax_rules = {
        "CN": {"rate": 0.13, "name": "增值税"},      # 中国 13%
        "US": {"rate": 0.07, "name": "销售税"},      # 美国约 7%
        "JP": {"rate": 0.10, "name": "消费税"},      # 日本 10%
    }

    rule = tax_rules.get(country, {"rate": 0, "name": "免税"})

    def calculate(price: float) -> float:
        """闭包：记住 country 和 tax_rules"""
        tax = price * rule["rate"]
        print(f"[{country}] {rule['name']}: {price:.2f} × {rule['rate']:.0%} = {tax:.2f}")
        return tax

    return calculate   # ← 返回的函数"记住了" rule 和 country


# 创建不同国家的计算器
cn_tax = make_tax_calculator("CN")
us_tax = make_tax_calculator("US")

# 各自计算——互不影响
cn_tax(100.0)   # [CN] 增值税: 100.00 × 13% = 13.00
us_tax(100.0)   # [US] 销售税: 100.00 × 7% = 7.00

# 验证闭包内容
print(cn_tax.__closure__)          # 闭包捕获了变量
print([cell.cell_contents for cell in cn_tax.__closure__])
```

---

## 5.4 lambda 匿名函数

**案例1：lambda 的常见用法**

```python
# 配合 sorted 的 key 参数
pairs = [(1, "one"), (2, "two"), (3, "three")]
pairs.sort(key=lambda p: p[1])      # 按第二个元素（字符串）排序
print(pairs)

# 配合 map（虽然推导式更 Pythonic）
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# 配合 filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)    # [2, 4]

# 注意：推导式通常更可读
squared2 = [x ** 2 for x in numbers]       # 比 map+lambda 更 Pythonic
evens2 = [x for x in numbers if x % 2 == 0]
```

**案例2：lambda 与闭包的经典陷阱**

```python
# ❌ 陷阱：lambda 捕获的是变量名，不是值
# 所有 lambda 共享同一个变量 i 的最终值
funcs_bad = []
for i in range(3):
    funcs_bad.append(lambda: i)      # 所有 lambda 都引用同一个 i

print([f() for f in funcs_bad])      # [2, 2, 2] —— 不是 [0, 1, 2]！

# ✅ 解决方案：用默认参数冻结当前值
funcs_good = []
for i in range(3):
    funcs_good.append(lambda i=i: i)  # i=i 在定义时求值，冻结了当前值

print([f() for f in funcs_good])     # [0, 1, 2] ← 正确！
```

**案例3：工业级 —— 用 lambda 字典替代 if-elif 链**

```python
from typing import Callable, Dict, Any

class MathOperation:
    """
    用 lambda 字典替代长 if-elif。
    新增操作只需加一行字典项，符合开闭原则。
    """

    # 操作字典：符号 → lambda
    _OPERATIONS: Dict[str, Callable[[float, float], float]] = {
        "+": lambda a, b: a + b,
        "-": lambda a, b: a - b,
        "*": lambda a, b: a * b,
        "/": lambda a, b: a / b if b != 0 else float("nan"),
        "^": lambda a, b: a ** b,
        "%": lambda a, b: a % b,
    }

    @classmethod
    def calculate(cls, expr: str) -> float:
        """
        解析简单表达式并计算。如: "3 + 5" → 8.0
        """
        parts = expr.strip().split()
        if len(parts) != 3:
            raise ValueError(f"表达式格式错误: {expr}")

        left, op, right = parts
        if op not in cls._OPERATIONS:
            raise ValueError(f"不支持的操作符: {op}")

        return cls._OPERATIONS[op](float(left), float(right))


# 使用
calc = MathOperation()
print(calc.calculate("10 + 5"))    # 15.0
print(calc.calculate("3 * 7"))     # 21.0
print(calc.calculate("2 ^ 10"))    # 1024.0
```

---

## 5.5 递归

**案例1：递归三要素——阶乘**

```python
# 递归三要素:
# 1. 终止条件（base case）
# 2. 缩小问题规模
# 3. 调用自身

def factorial(n: int) -> int:
    """n! = n × (n-1) × ... × 1"""
    # 1. 终止条件
    if n <= 1:
        return 1
    # 2+3. 缩小规模 + 调用自身
    return n * factorial(n - 1)

print(factorial(5))  # 120
```

**案例2：递归遍历树形结构**

```python
from typing import List, Dict, Any

def traverse_tree(node: Dict[str, Any], path: str = ""):
    """
    递归遍历树形结构（文件系统、组织架构、JSON 等）。
    """
    name = node.get("name", "unknown")
    current_path = f"{path}/{name}" if path else name

    print(f"📁 {current_path}")

    # 递归处理子节点
    for child in node.get("children", []):
        traverse_tree(child, current_path)


# 模拟公司组织架构
org_chart = {
    "name": "CEO",
    "children": [
        {
            "name": "CTO",
            "children": [
                {"name": "前端组", "children": [
                    {"name": "小张"}, {"name": "小李"}
                ]},
                {"name": "后端组", "children": [
                    {"name": "小王"}, {"name": "小赵"}
                ]},
            ]
        },
        {
            "name": "CFO",
            "children": [
                {"name": "财务组"},
                {"name": "审计组"},
            ]
        },
    ]
}

# traverse_tree(org_chart)
```

**案例3：工业级 —— 用栈模拟递归避免栈溢出**

```python
from typing import List, Dict, Any, Iterator
import os
from pathlib import Path

def walk_directory_iterative(root: str) -> Iterator[str]:
    """
    用栈遍历目录树（迭代方式，不会栈溢出）。
    处理百万级文件时，递归可能超过 sys.getrecursionlimit()。
    """
    stack = [root]

    while stack:
        current = stack.pop()

        # 如果是目录，把子项压入栈
        if os.path.isdir(current):
            try:
                entries = os.listdir(current)
            except PermissionError:
                continue
            for entry in entries:
                stack.append(os.path.join(current, entry))

        # 返回文件路径
        yield current


# 统计目录下的文件（与递归方法对比）
def count_files_recursive(path: str) -> int:
    """递归统计（可能栈溢出）"""
    count = 0
    if os.path.isfile(path):
        return 1
    if os.path.isdir(path):
        try:
            for entry in os.listdir(path):
                count += count_files_recursive(os.path.join(path, entry))
        except PermissionError:
            pass
    return count

def count_files_iterative(path: str) -> int:
    """迭代统计（不会栈溢出）"""
    return sum(1 for p in walk_directory_iterative(path) if os.path.isfile(p))


# 对比（在实际大目录上测试）
# print(count_files_recursive("."))
# print(count_files_iterative("."))
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| 参数传递 | 传对象引用——可变对象会被修改，不可变不会 |
| 默认参数陷阱 | 默认值只在定义时求值一次——用 `None` 替代可变默认值 |
| `*args` | 接收多余位置参数，打包成元组 |
| `**kwargs` | 接收多余关键字参数，打包成字典 |
| `/` | 之前的参数只能按位置传 (3.8+) |
| `*` | 之后的参数只能按关键字传 |
| LEGB | 查找顺序: Local → Enclosing → Global → Built-in |
| 闭包 | 函数记住它被创建时的环境（外部变量） |
| `nonlocal` | 声明使用外层函数的变量（而非创建新的局部变量） |
| 装饰器 | `@decorator` = `func = decorator(func)` |
| 递归 | 三要素：终止条件 + 缩小规模 + 调用自身 |
