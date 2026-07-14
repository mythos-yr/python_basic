# 第五章：函数 —— 抽象的第一层

---

## 5.1 函数是什么

### 理论：为什么需要函数？

函数解决两个核心问题：

1. **消除重复**：同样的逻辑不用写多遍
2. **抽象复杂度**：给一段逻辑起个名字，调用方只需要知道"做什么"，不需要知道"怎么做"

**类比**：`print()` 是一个函数。你不需要知道它内部怎么跟操作系统交互、怎么把字符渲染到终端——你只需要知道"调用 print 就能在屏幕上看到东西"。

---

### 关键字/语法

```python
def 函数名(参数1, 参数2):
    """文档字符串（可选，但推荐写）"""
    # 函数体
    return 返回值  # 可省略，省略时返回 None
```

| 关键字 | 作用 |
|--------|------|
| `def` | 定义函数 |
| `return` | 返回一个值，并**立即结束**函数执行 |
| `lambda` | 创建匿名函数（只能写一行表达式） |

---

### 案例

**案例1：定义和调用函数**

```python
def greet(name, greeting="Hello"):
    """向某人打招呼"""
    return f"{greeting}, {name}!"

print(greet("Alice"))                # Hello, Alice!
print(greet("Bob", greeting="Hi"))   # Hi, Bob!
```

**案例2：Python 函数是一等公民——可以当参数传递**

```python
def apply(func, value):
    return func(value)

print(apply(str.upper, "hello"))  # HELLO
print(apply(len, [1, 2, 3]))     # 3
```

**案例3：return 立即结束函数（后面代码不会执行）**

```python
def safe_divide(a, b):
    if b == 0:
        return "错误：除数为零"  # 函数在此结束
    return a / b                 # b != 0 才执行到这里

print(safe_divide(10, 2))  # 5.0
print(safe_divide(10, 0))  # 错误：除数为零
```

---

## 5.2 参数传递

### 理论：Python 是"传对象引用"（Call by Sharing）

这是最容易被误解的概念。Python 参数既不是传值，也不是传引用，而是**把实参对象的引用传给形参**。

很简单：**函数内部对可变对象的内容修改会影响外部；对参数的重新赋值不会影响外部。**

```
传值（C语言风格）：函数拿到的是副本，修改不影响外部
传对象引用（Python）：函数拿到的是同一个对象的引用
  - 如果对象不可变（int, str, tuple），"修改"会创建新对象 → 不影响外部
  - 如果对象可变（list, dict），修改内容会影响外部
  - 重新赋值（=）是换标签，不影响外部
```

**类比**：你给朋友一个快递包裹号（引用）。你朋友可以打开包裹修改里面的东西（可变对象），也可以把包裹号改成另一个包裹（重新赋值），但不会影响你手里的包裹号。

---

### 关键字/语法

**参数定义的全部规则**（按顺序）：

```python
def func(位置参数, /, 位置或关键字, *, 仅限关键字, **kwargs):
    pass
```

| 符号 | 含义 | 例子 |
|------|------|------|
| 无修饰 | 位置或关键字参数 | `def f(x)` |
| `/` 之前 | **只能**按位置传（Python 3.8+） | `def f(x, /)` |
| `*` 之后 | **只能**按关键字传 | `def f(*, key)` |
| `*args` | 收集多余的位置参数（打包成元组） | `def f(*args)` |
| `**kwargs` | 收集多余的关键字参数（打包成字典） | `def f(**kwargs)` |

**解包调用**（调用时用 `*` 和 `**` 拆开容器）：

```python
nums = [1, 2, 3]
func(*nums)          # 等价于 func(1, 2, 3)

info = {"name": "A", "age": 30}
func(**info)         # 等价于 func(name="A", age=30)
```

---

### 案例

**案例1：可变对象、不可变对象作为参数的区别**

```python
# 不可变参数：函数内"修改"不影响外部
def add_one(x):
    x = x + 1         # 创建了新对象，x 重新绑定

n = 5
add_one(n)
print(n)              # 5 —— 没变

# 可变参数：函数内修改内容会影响外部
def append_one(lst):
    lst.append(1)     # 修改原对象的内容！

a = [1, 2]
append_one(a)
print(a)              # [1, 2, 1] —— 变了！
```

**案例2：默认参数的陷阱和正确做法**

```python
# ❌ 默认参数在函数定义时只求值一次！
def bad(item, target=[]):
    target.append(item)
    return target

print(bad(1))  # [1]
print(bad(2))  # [1, 2] —— 同一个 list！

# ✅ 用 None + 内部初始化
def good(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

**案例3：keyword-only 参数——让函数调用更安全**

```python
# * 后面的参数只能用关键字传，防止混淆
def create_user(name, *, age, email=None):
    return {"name": name, "age": age, "email": email}

# ✅ 清晰
create_user("Alice", age=30, email="a@example.com")
# ❌ 报错：age 必须用关键字
# create_user("Alice", 30, "a@example.com")
```

---

## 5.3 作用域 (Scope)

### 理论：变量在哪里生效？

Python 查找变量遵循 **LEGB** 规则，按这个顺序逐级查找：

```
Local     → 函数内部定义的变量
Enclosing → 外层函数中定义的变量（闭包场景）
Global    → 模块级别的变量
Built-in  → Python 内置的名字（print, len 等）
```

找到就停止，找不到就报 `NameError`。

**关键坑**：在函数内给变量赋值时，Python 默认把它当做**局部变量**。如果想修改外层变量，必须用 `global` 或 `nonlocal` 声明。

---

### 关键字/语法

| 关键字 | 作用 | 使用场景 |
|--------|------|----------|
| `global x` | 声明 x 引用全局变量 | 在函数内修改全局变量 |
| `nonlocal x` | 声明 x 引用外层函数的变量 | 在闭包内修改外层变量 |

---

### 案例

**案例1：LEGB 查找顺序演示**

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        # 注释掉下面这行，看 x 会找哪一级
        # x = "local"
        print(x)       # 先找 local（没有）→ enclosing → global

    inner()

outer()  # 输出: enclosing
```

**案例2：nonlocal——闭包计数器**

```python
def make_counter():
    count = 0            # enclosing 变量

    def increment():
        nonlocal count   # 没有这行，count += 1 会报错！
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

**案例3：global——修改全局变量（少用）**

```python
config = {"debug": False}

def enable_debug():
    global config       # 声明要用的是全局的 config
    config = {"debug": True}   # 如果不加 global，这会创建局部变量
```

---

## 5.4 装饰器 (Decorator)

### 理论：不改函数内部代码，给函数"加功能"

装饰器本质是一个**接受函数、返回新函数**的高阶函数。

```python
@decorator
def func():
    pass

# 等价于：
func = decorator(func)
```

**类比**：手机壳。手机本身（被装饰的函数）不变，套上壳（装饰器）就有了防摔、支架等新功能。

---

### 关键字/语法

| 关键字 | 作用 |
|--------|------|
| `@decorator` | 装饰器语法糖 |
| `@functools.wraps(func)` | 保留被装饰函数的元信息（名字、文档字符串等） |

**装饰器的嵌套层级**：
- 无参数装饰器：2 层嵌套
- 带参数装饰器：3 层嵌套

---

### 案例

**案例1：最简单的装饰器——计时**

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)               # 保留 func 的名字和文档
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 耗时: {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(0.5)
    return "done"

slow_function()  # slow_function 耗时: 0.5001s
```

**案例2：带参数的装饰器——重试机制**

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1.0):
    """带参数：重试失败的操作"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"第{attempt}次失败: {e}，{delay}s后重试")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def unstable_api():
    import random
    if random.random() < 0.7:
        raise ConnectionError("网络波动")
    return "success"
```

**案例3：多个装饰器的执行顺序——由内到外**

```python
def deco_a(func):
    print("A 包装开始")
    def wrapper(*args, **kwargs):
        print("A 执行前")
        result = func(*args, **kwargs)
        print("A 执行后")
        return result
    return wrapper

def deco_b(func):
    print("B 包装开始")
    def wrapper(*args, **kwargs):
        print("B 执行前")
        result = func(*args, **kwargs)
        print("B 执行后")
        return result
    return wrapper

@deco_a
@deco_b
def say_hello():
    print("Hello!")

# 等价于: say_hello = deco_a(deco_b(say_hello))
# 包装顺序: B 先包装，A 再包装
# 执行顺序: A 前 → B 前 → 函数体 → B 后 → A 后
```

---

## 5.5 lambda 匿名函数

### 理论：给"只用一次"的简单逻辑一个轻量写法

lambda 就是 `def` 的极简版，只能写**单行表达式**，不能包含语句（if/for/赋值等）。

**适用场景**：作为 `sorted()` 的 key、`map()`/`filter()` 的回调。

**注意**：如果 lambda 开始变复杂，或者需要复用，就用 `def`。不要为了省一行把代码搞得不清晰。

---

### 关键字/语法

```python
lambda 参数: 表达式    # 只能一行，表达式的值自动返回
```

---

### 案例

**案例1：lambda 配合 sorted/filter/map**

```python
# sorted 的 key
pairs = [(1, "one"), (2, "two"), (3, "three")]
pairs.sort(key=lambda p: p[1])   # 按第二个元素排序

# 注意：推导式通常比 map/filter + lambda 更 Pythonic
nums = [1, 2, 3, 4, 5]
# map + lambda —— 能工作，但不是最 Pythonic 的
squares = list(map(lambda x: x**2, nums))
# 推导式 —— 更推荐
squares = [x**2 for x in nums]
```

**案例2：经典陷阱——lambda 捕获变量名而非值**

```python
# ❌ 所有 lambda 共享同一个变量 i 的最终值
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])  # [2, 2, 2]

# ✅ 用默认参数冻结当前值
funcs = [lambda i=i: i for i in range(3)]
print([f() for f in funcs])  # [0, 1, 2]
```

**案例3：用 lambda 字典替代 if-elif 链**

```python
# 操作符 → lambda 映射（比长串 if-elif 更优雅）
operations = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b if b != 0 else float("nan"),
}
print(operations["*"](6, 7))  # 42
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| `def` | 定义函数 |
| `return` | 返回值并结束函数 |
| `yield` | 暂停函数，返回值，可继续（见第6章） |
| 参数传递 | 传对象引用；可变对象内容可被修改 |
| `*args` | 收集多余位置参数 → 元组 |
| `**kwargs` | 收集多余关键字参数 → 字典 |
| `/` | 前面的参数只能按位置传 |
| `*` | 后面的参数只能按关键字传 |
| LEGB | 变量查找：Local → Enclosing → Global → Built-in |
| `global` | 声明修改全局变量 |
| `nonlocal` | 声明修改外层函数变量 |
| `@decorator` | 装饰器：接受函数，返回增强后的函数 |
| `lambda` | 单行匿名函数 |
