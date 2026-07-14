# 第五章：函数 —— 抽象的第一层

---

## 5.1 函数是什么

### 理论：为什么需要函数？

两个核心价值：
1. **消除重复**：同样的逻辑写一次，到处调用
2. **抽象复杂度**：调用方只需要知道"做什么"，不需要知道"怎么做"

**类比**：`print()` 就是函数。你不需要知道它内部如何处理操作系统调用、字符编码、终端渲染——你用的时候只写 `print("hello")`。

**函数是一等公民**：在 Python 中，函数本身就是对象——可以赋值给变量、作为参数传递、作为返回值返回。

---

### 关键字/语法

```python
def 函数名(参数1, 参数2):
    """文档字符串（可选但推荐）—— 用 help() 可查看"""
    # 函数体
    return 返回值  # 可省略，省略时默认返回 None
```

| 关键字 | 作用 |
|--------|------|
| `def` | 定义函数 |
| `return` | 返回值并**立即终止**函数（无 return 时自动返回 None） |
| `lambda` | 创建匿名函数（只能写单行表达式） |
| `yield` | 暂停函数并返回值，可恢复（见第6章） |

---

### 案例

**案例1：函数的基本定义、文档字符串、默认参数**

```python
def greet(name, greeting="Hello"):
    """向指定的人打招呼。

    Args:
        name: 对方的名字
        greeting: 问候语，默认 "Hello"
    """
    return f"{greeting}, {name}!"

print(greet("Alice"))                # Hello, Alice!
print(greet("Bob", greeting="Hi"))   # Hi, Bob!
# help(greet) 可以查看文档字符串
```

**案例2：函数是一等公民——可赋值、可传参、可返回**

```python
# 赋值给变量
def add(a, b):
    return a + b

my_add = add          # 函数赋值给变量
print(my_add(3, 5))   # 8

# 作为参数传递
def apply(func, value):
    return func(value)

print(apply(str.upper, "hello"))  # HELLO
print(apply(len, [1, 2, 3]))     # 3

# 作为返回值
def make_adder(n):
    def adder(x):
        return x + n
    return adder      # 返回一个函数

add_10 = make_adder(10)
print(add_10(5))      # 15
```

**案例3：return 立即结束函数——用于提前退出/守卫**

```python
def safe_divide(a, b):
    """安全除法——提前 return 处理边界条件"""
    if b == 0:
        return "错误：除数不能为零"  # 函数在此结束
    if not isinstance(b, (int, float)):
        return "错误：类型不匹配"
    return a / b                      # 一切正常才到这里

print(safe_divide(10, 2))   # 5.0
print(safe_divide(10, 0))   # 错误：除数不能为零
print(safe_divide(10, "a")) # 错误：类型不匹配
```

---

## 5.2 参数传递

### 理论：Python 是"传对象引用"

Python 参数既不是传值，也不是传引用，而是**把实参对象的引用传给形参**。

核心规则很简单：
- 函数内**修改可变对象的内容** → 影响外部
- 函数内**对形参重新赋值** → 不影响外部

```
类比：你给朋友一个包裹号（引用）。
  朋友可以打开包裹修改里面的东西（修改可变对象）
  也可以把包裹号换成另一个包裹的（重新赋值）
  但不影响你自己手里的包裹号
```

---

### 知识点：参数定义的全部规则

按以下顺序定义参数：

```python
def func(仅限位置, /, 位置或关键字, *, 仅限关键字):
    pass
```

| 位置 | 写法 | 调用时必须 |
|------|------|-----------|
| `/` 之前 | `def f(x, /)` | 只能按位置传 `f(1)` |
| 默认位置 | `def f(x)` | 位置或关键字都行 `f(1)` 或 `f(x=1)` |
| `*` 之后 | `def f(*, x)` | 只能按关键字传 `f(x=1)` |
| `*args` | `def f(*args)` | 收集多余位置参数 → 元组 |
| `**kwargs` | `def f(**kwargs)` | 收集多余关键字参数 → 字典 |

**解包调用**（调用时拆开容器）：

```python
nums = [1, 2, 3];  info = {"age": 30}
func(*nums)          # 等价 func(1, 2, 3)
func(**info)         # 等价 func(age=30)
```

---

### 案例

**案例1：不可变 vs 可变参数的差异**

```python
# 不可变参数："修改" = 创建新对象 → 不影响外部
def add_one(x):
    x = x + 1         # 创建新对象，x 重新绑定
n = 5; add_one(n)
print(n)               # 5 —— 没变

# 可变参数：修改内容 → 影响外部
def append_one(lst):
    lst.append(1)     # 修改原对象
a = [1, 2]; append_one(a)
print(a)               # [1, 2, 1] —— 变了！
```

**案例2：默认参数陷阱 + 正确做法**

```python
# ❌ 默认参数在定义时只求值一次，所有调用共享同一个对象
def bad(item, target=[]):
    target.append(item)
    return target
print(bad(1))  # [1]
print(bad(2))  # [1, 2]  ← 同一个列表！

# ✅ 用 None 做哨兵值
def good(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

**案例3：keyword-only 让 API 调用更安全**

```python
# * 之后的参数只能用关键字传——防止语义混淆
def create_user(name, *, age, email=None, phone=None):
    return {"name": name, "age": age, "email": email}

# ✅ 一目了然：哪个是 age，哪个是 email
user = create_user("Alice", age=30, email="a@example.com")
# ❌ create_user("Alice", 30, "a@example.com")  — 报错
```

**案例4：`*args` 和 `**kwargs`——万能函数签名**

```python
def log_all(*args, **kwargs):
    """接收任意数量和形式的参数"""
    print(f"位置参数: {args}")     # 元组
    print(f"关键字参数: {kwargs}")  # 字典

log_all(1, 2, 3, name="Alice", age=30)
# 位置参数: (1, 2, 3)
# 关键字参数: {'name': 'Alice', 'age': 30}

# 转发参数的标准模式（装饰器、子类方法中常用）
def wrapper(*args, **kwargs):
    # 打日志、做校验...
    return original_func(*args, **kwargs)
```

---

## 5.3 作用域与闭包

### 理论：变量在哪里生效？

Python 按 **LEGB** 顺序查找变量：

```
Local     → 当前函数内部
Enclosing → 外层函数（闭包场景）
Global    → 模块级别
Built-in  → Python 内置（print, len, range...）
```

**关键坑**：在函数内给变量赋值时，Python 默认创建局部变量。想修改外层变量，必须用 `global` 或 `nonlocal` 声明。

**闭包**：内层函数"记住"了它被创建时外层函数的变量——即使外层函数已经返回。

---

### 关键字/语法

| 关键字 | 作用 | 示例 |
|--------|------|------|
| `global x` | 声明 x 引用全局变量 | 函数内修改模块级变量 |
| `nonlocal x` | 声明 x 引用外层函数变量 | 闭包内修改外层变量 |

---

### 案例

**案例1：LEGB 查找顺序——逐级向上找**

```python
x = "global"            # Global

def outer():
    x = "enclosing"     # Enclosing（对于 inner 而言）

    def inner():
        # 依次找 Local → Enclosing → Global
        print(x)         # "enclosing"——在 Enclosing 层找到了

    inner()

outer()
```

**案例2：nonlocal——闭包内修改外层变量**

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count      # 声明引用的不是局部变量
        count += 1          # 没有 nonlocal 这行会报 UnboundLocalError
        return count

    return increment        # 返回闭包——"记住"了 count

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3

# 窥探闭包内部
print(counter.__closure__)                         # 闭包捕获的变量
print(counter.__closure__[0].cell_contents)        # 当前 count 的值
```

**案例3（工业级）：用闭包实现不同国家的税率计算器**

```python
def make_tax_calculator(country: str, rate: float):
    """每个闭包"记住"自己的国家和税率"""
    def calculate(price: float) -> float:
        tax = price * rate
        print(f"[{country}] 税率 {rate:.0%}: {price} → 税额 {tax:.2f}")
        return tax
    return calculate

cn_tax = make_tax_calculator("中国", 0.13)
us_tax = make_tax_calculator("美国", 0.07)

cn_tax(100)   # [中国] 税率 13%: 100 → 税额 13.00
us_tax(100)   # [美国] 税率 7%: 100 → 税额 7.00
```

---

## 5.4 装饰器 (Decorator)

### 理论：给函数加功能，但不动函数内部代码

装饰器本质上是一个**接受函数、返回新函数**的高阶函数。

```python
@decorator
def func():
    pass

# 等价于: func = decorator(func)
```

**类比**：手机壳。手机本身不变，套上壳就有了新的功能。装饰器就是这个"壳"。

**层级关系**：
- 无参数装饰器（如 `@timer`）→ 2 层嵌套
- 带参数装饰器（如 `@retry(max=3)`）→ 3 层嵌套

---

### 关键字/语法

| 语法 | 作用 |
|------|------|
| `@decorator` | 装饰器语法糖 |
| `@functools.wraps(func)` | **必须加！** 保留被装饰函数的 `__name__`、`__doc__` 等元信息 |
| `@decorator(args)` | 先调用 `decorator(args)` 返回真正的装饰器，再装饰 |

**多个装饰器的执行顺序**：

```python
@a
@b
def f(): ...

# 等价于 f = a(b(f))
# 包装时：b 先包装，a 再包装（由内到外）
# 执行时：a 的 wrapper 先执行，然后 b 的 wrapper，然后原函数（像洋葱层层剥开）
```

---

### 案例

**案例1：计时装饰器——经典的无参数装饰器**

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)               # ← 必须加！否则 func.__name__ 会变成 "wrapper"
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[{func.__name__}] {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_work():
    time.sleep(0.5)
    return "done"

print(slow_work())             # [slow_work] 0.5001s \n done
print(slow_work.__name__)      # "slow_work" —— wraps 保留了原名字
```

**案例2：带参数装饰器——重试机制（3层嵌套）**

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1.0):
    """重试装饰器——max_attempts 和 delay 是装饰器的参数"""
    def decorator(func):               # 第2层：真正的装饰器
        @wraps(func)                   # 第3层：wrapper
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise          # 最后一次也失败，抛出异常
                    print(f"第{attempt}次失败: {e}，{delay}s 后重试...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.2)
def call_api():
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络波动")
    return "OK"
```

**案例3：装饰器在 Web 框架中的经典用法——登录检查**

```python
from functools import wraps

# 模拟当前登录用户
current_user = None

def login_required(func):
    """要求登录才能访问的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user is None:
            raise PermissionError("请先登录")
        return func(*args, **kwargs)
    return wrapper

@login_required
def view_profile():
    return f"{current_user} 的个人资料"

# view_profile()  # 如果 current_user 为 None → PermissionError
```

---

## 5.5 lambda 匿名函数

### 理论：轻量的一次性函数

lambda 就是 `def` 的极简版：只能写**单行表达式**，表达式的值自动返回。不能包含赋值、if/for 等语句。

**何时用**：作为 `sorted()` 的 key、简短的回调。一旦逻辑开始复杂或需要复用 → 用 `def`。

---

### 案例

**案例1：lambda 配合 sorted / filter / map**

```python
# sorted 的 key —— lambda 最常见的用途
pairs = [(1, "one"), (2, "two"), (3, "three")]
pairs.sort(key=lambda p: p[1])    # 按第二个元素排序
print(pairs)

# 注意：下面的推导式比 map+lambda 更 Pythonic
nums = [1, 2, 3, 4, 5]
# 可用但不推荐
squares = list(map(lambda x: x**2, nums))
# 推荐
squares = [x**2 for x in nums]
```

**案例2：经典陷阱——lambda 捕获的是变量名不是值**

```python
# ❌ 所有 lambda 共享同一个 i（最终值 2）
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # [2, 2, 2]

# ✅ 用默认参数"冻结"当前值
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])   # [0, 1, 2]
```

**案例3：用 lambda 字典替代 if-elif 链**

```python
operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else float("nan"),
}
print(operations["*"](6, 7))  # 42
# 比一长串 if-elif 更清晰，新增操作只需加一行
```

---

## 5.6 递归

### 理论：函数调用自身

递归三要素：
1. **终止条件**（base case）—— 什么时候停下来
2. **缩小规模** —— 每次调用让问题"变小"
3. **调用自身** —— 用缩小后的问题调自己

**注意**：Python 有递归深度限制（默认 ~1000），可用 `sys.setrecursionlimit()` 调整。深度太深会栈溢出。

---

### 案例

**案例1：经典递归——阶乘和斐波那契**

```python
def factorial(n):
    if n <= 1:             # 终止条件
        return 1
    return n * factorial(n - 1)  # 缩小 + 调用自身

print(factorial(5))  # 120

def fibonacci(n):
    if n <= 1:             # 终止条件
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # 两个子问题

print(fibonacci(10))  # 55
# 注意：这个实现效率极低（重复计算），实际请用 lru_cache
```

**案例2：递归遍历树形结构**

```python
def traverse_tree(node, depth=0):
    """递归遍历任意深度的嵌套结构"""
    indent = "  " * depth
    print(f"{indent}📁 {node['name']}")
    for child in node.get("children", []):
        traverse_tree(child, depth + 1)

org = {
    "name": "CEO",
    "children": [
        {"name": "CTO", "children": [{"name": "前端"}, {"name": "后端"}]},
        {"name": "CFO"},
    ]
}
# traverse_tree(org)  # 递归打印整个组织架构
```

**案例3：用迭代（栈）替代递归避免栈溢出**

```python
# 递归遍历深层目录可能栈溢出 → 用栈迭代
def walk_tree_iterative(root):
    stack = [root]
    while stack:
        node = stack.pop()
        print(node["name"])
        for child in reversed(node.get("children", [])):
            stack.append(child)    # 压入栈（后进先出）
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| `def` / `return` | 定义函数/返回值并结束 |
| 参数传递 | 传对象引用：可变改内容影响外面，赋值不影响 |
| `*args` | 收集多余位置参数 → 元组 |
| `**kwargs` | 收集多余关键字参数 → 字典 |
| `/` / `*` | `/` 前只能位置；`*` 后只能关键字 |
| LEGB | 变量查找：Local → Enclosing → Global → Built-in |
| `global` / `nonlocal` | 声明修改全局/外层变量 |
| 闭包 | 函数"记住"创建时的环境变量 |
| `@decorator` | 包装函数，增强功能（接受函数，返回函数） |
| `@wraps(func)` | 保留被装饰函数的元信息（**必须加**） |
| `lambda` | 单行匿名函数（简单则用，复杂则 def） |
| 递归 | 三要素：终止条件 + 缩小规模 + 调用自身 |
