# 第十章：面向对象编程 (OOP)

---

## 10.1 类和对象——把事物抽象成代码

### 理论：为什么需要面向对象？

当代码里出现了**一组函数总是操作同一组数据**时，就是该用类的时候。面向对象把相关的数据和操作**打包**在一起。

**四个核心概念**：

| 概念 | 含义 | 类比 |
|------|------|------|
| 类 (class) | 创建对象的模板 | 汽车设计图 |
| 对象/实例 (instance) | 按模板造出来的具体东西 | 你开的那辆具体的车 |
| 属性 (attribute) | 对象拥有的数据 | 颜色、速度、油量 |
| 方法 (method) | 对象能做什么 | 加速、刹车、鸣笛 |

---

### 关键字/语法

```python
class 类名:
    """文档字符串"""

    类属性 = 值               # 所有实例共享

    def __init__(self, 参数):
        self.实例属性 = 参数   # 每个实例独立

    def 方法(self, 参数):
        pass                 # self = 调用这个方法的那个实例
```

| 关键字 | 作用 |
|--------|------|
| `class` | 定义类 |
| `__init__(self)` | 构造方法，`obj = Cls(args)` 时自动调用 |
| `self` | 自动指向调用方法的实例。`obj.m()` = `Cls.m(obj)` |
| `@classmethod` | 类方法：第一个参数是 `cls`（类本身），不依赖实例 |
| `@staticmethod` | 静态方法：不需要 `self` 或 `cls`，只是放在类里的普通函数 |

**`self` 的本质**：`obj.method(arg)` 被 Python 转换为 `ClassName.method(obj, arg)`。

---

### 案例

**案例1：基础类的完整写法**

```python
class Dog:
    species = "Canis familiaris"   # 类属性——所有实例共享

    def __init__(self, name, age):
        self.name = name            # 实例属性——每只狗不同
        self.age = age

    def bark(self):                 # 实例方法——self 是调用者
        return f"{self.name}: 汪汪！"

d1 = Dog("旺财", 3)
d2 = Dog("来福", 5)
print(d1.bark())        # 旺财: 汪汪！
print(d1.species)       # Canis familiaris
print(d2.species)       # 同一个类属性
```

**案例2：类属性 vs 实例属性——可变类属性的陷阱**

```python
# ❌ 可变类属性：所有实例共享同一个列表！
class Team:
    members = []

    def __init__(self, name):
        self.name = name

a = Team("A队"); b = Team("B队")
a.members.append("张三")            # 看起来只改了 a
print(b.members)                     # ['张三'] —— b 也被"影响"了！

# ✅ 正确：在 __init__ 中初始化实例属性
class TeamFixed:
    def __init__(self, name):
        self.name = name
        self.members = []
```

**案例3：@classmethod 和 @staticmethod 的区别**

```python
class MyClass:
    class_var = 0

    def instance_method(self):
        """需要 self，能访问实例属性和类属性"""
        return f"实例方法, class_var={self.class_var}"

    @classmethod
    def class_method(cls):
        """需要 cls，只能访问类属性，常用作'替代构造器'"""
        cls.class_var += 1
        return f"类方法, class_var={cls.class_var}"

    @staticmethod
    def static_method(x, y):
        """不需要 self 或 cls——和普通函数一样，只是放在类里方便组织"""
        return x + y

# 使用对比
obj = MyClass()
print(obj.instance_method())          # 通过实例调用
print(MyClass.class_method())         # 通过类调用（推荐）
print(MyClass.static_method(3, 5))    # 8
```

**案例4：@dataclass——一行装饰器替代所有样板代码**

```python
from dataclasses import dataclass, field
from typing import List

# ❌ 传统：__init__, __repr__, __eq__ 全要手写几十行

# ✅ @dataclass：自动生成
@dataclass
class User:
    name: str
    age: int
    email: str = ""
    tags: List[str] = field(default_factory=list)  # 可变默认值必须这样写

u1 = User("Alice", 30)
u2 = User("Alice", 30)
print(u1)                   # User(name='Alice', age=30, email='')
print(u1 == u2)             # True（自动生成的 __eq__）
```

---

## 10.2 封装——控制访问权限

### 理论：Python 靠约定不靠强制

Python 没有 private/public 关键字，靠**命名约定**控制可见性：

| 写法 | 含义 | 实际效果 |
|------|------|----------|
| `name` | 公开属性 | 随便访问 |
| `_name` | 约定"内部使用" | 不强制，IDE 会提示 |
| `__name` | 名称改写 (name mangling) | 变成 `_ClassName__name`，防止子类意外覆盖 |

**property**：让方法像属性一样被访问。外部用 `obj.value` 而不是 `obj.get_value()`，同时内部保留校验逻辑。

---

### 关键字/语法

```python
@property        # getter：读取时调用
@xxx.setter      # setter：赋值时调用（可加校验）
@xxx.deleter     # deleter：del 时调用
```

---

### 案例

**案例1：下划线约定的实际行为**

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner          # 公开
        self._balance = balance     # 约定"内部属性"
        self.__pin = "1234"         # 名称改写

acc = BankAccount("Alice", 1000)
print(acc._balance)                 # 能访问，但 IDE 会警告你
# print(acc.__pin)                  # AttributeError!
print(acc._BankAccount__pin)        # "1234" —— 改写后还是能访问
```

**案例2：@property——带校验的属性**

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius

    @property
    def celsius(self):              # getter
        return self._celsius

    @celsius.setter
    def celsius(self, value):       # setter（赋值时校验）
        if value < -273.15:
            raise ValueError("低于绝对零度！")
        self._celsius = value

    @property
    def fahrenheit(self):           # 只读属性（无 setter）
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.celsius)        # 25    —— 不需要 t.celsius()
t.celsius = 30          # 自动调 setter 校验
# t.fahrenheit = 90     # AttributeError —— 只读！
```

**案例3（工业级）：描述符——可复用的字段验证（Django ORM 原理）**

```python
class ValidatedField:
    """类级别的字段校验——一次定义，到处复用"""
    def __init__(self, field_type):
        self.field_type = field_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"       # Python 3.6+ 自动设置属性名

    def __get__(self, obj, owner=None):
        return getattr(obj, self.name, None) if obj else self

    def __set__(self, obj, value):
        if not isinstance(value, self.field_type):
            raise TypeError(f"{self.name[1:]} 需要 {self.field_type.__name__}")
        setattr(obj, self.name, value)

class User:
    name = ValidatedField(str)
    age = ValidatedField(int)

    def __init__(self, name, age):
        self.name = name; self.age = age  # 触发描述符

# User("Alice", "三十")  # TypeError!
```

---

## 10.3 魔术方法——让自定义对象像内置类型一样工作

### 理论

以 `__` 开头和结尾的方法叫魔术方法（dunder methods）。实现它们，你的对象就能使用 `len()`、`str()`、`+`、`in`、`for` 等内置操作。

---

### 知识点：常用魔术方法速查

| 魔术方法 | 触发方式 | 作用 |
|----------|---------|------|
| `__str__(self)` | `str(obj)`, `print(obj)` | 给**用户**看的字符串 |
| `__repr__(self)` | `repr(obj)`, 交互环境直接输入 | 给**开发者**看的（应能"重现"对象） |
| `__len__(self)` | `len(obj)` | 返回容器长度 |
| `__eq__(self, o)` | `a == b` | 相等比较 |
| `__lt__(self, o)` | `a < b` | 小于比较（排序用） |
| `__add__(self, o)` | `a + b` | 加法 |
| `__getitem__(self, i)` | `obj[i]` | 按索引取值 |
| `__setitem__(self, i, v)` | `obj[i] = v` | 按索引设值 |
| `__contains__(self, x)` | `x in obj` | 成员判断 |
| `__iter__(self)` | `for x in obj` | 使对象可迭代 |
| `__call__(self, ...)` | `obj(...)` | 让实例像函数一样被调用 |
| `__enter__`/`__exit__` | `with obj:` | 上下文管理器 |
| `__hash__(self)` | `hash(obj)` | 使对象可哈希（可做 dict 的键） |
| `__new__(cls, ...)` | 在 `__init__` **之前**调用 | 控制对象创建（单例模式） |
| `__slots__` | 类变量 `__slots__ = ("a","b")` | 限制实例属性，节省内存 |

**`__str__` vs `__repr__`**：如果只实现 `__repr__`，`__str__` 会回退到 `__repr__`。所以至少实现 `__repr__`。

---

### 案例

**案例1：让自定义对象支持打印、比较、运算**

```python
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

p1 = Point(3, 4); p2 = Point(1, 2)
print(p1)            # Point(3, 4)
print(p1 == p2)      # False
print(p1 + p2)       # Point(4, 6)
print(abs(p1))       # 5.0
```

**案例2：模拟容器——让对象能用 [ ] 和 for**

```python
class HistoryList:
    def __init__(self):
        self._data = []
    def append(self, item):
        self._data.append(item)
    def __getitem__(self, i):
        return self._data[i]
    def __len__(self):
        return len(self._data)
    def __contains__(self, x):
        return x in self._data
    def __iter__(self):
        return iter(self._data)

hl = HistoryList()
hl.append("A"); hl.append("B"); hl.append("C")
print(len(hl))       # 3
print(hl[1])         # B
print("B" in hl)     # True
print([x for x in hl])  # ['A', 'B', 'C']
```

**案例3：`__new__` vs `__init__`——控制对象创建（单例模式）**

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)   # 真正创建对象
        return cls._instance                       # 永远返回同一个

    def __init__(self, value=None):
        if value is not None:
            self.value = value  # 只在首次初始化时设值

a = Singleton("first")
b = Singleton("second")
print(a is b)            # True —— 同一个对象！
print(a.value, b.value)  # first first
```

**案例4：`__slots__`——节省内存，禁用动态属性**

```python
import sys

class Regular:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Slotted:
    __slots__ = ("x", "y")        # 只允许 x 和 y 两个属性
    def __init__(self, x, y):
        self.x, self.y = x, y

r = Regular(1, 2); s = Slotted(1, 2)
print(sys.getsizeof(r.__dict__))  # ~104 字节（有 __dict__）
# s 没有 __dict__，实例内存节省约 50%

# r.z = 3    # ✅ 可以动态添加属性
# s.z = 3    # ❌ AttributeError —— slots 禁用了动态属性
```

---

## 10.4 继承——利用已有的，扩展自己的

### 理论：is-a 用继承，has-a 用组合

如果 B 是 A 的一种（猫是动物），用**继承**。如果 B 包含 A（汽车包含引擎），用**组合**。

**MRO**：多继承时，Python 按 C3 线性化算法决定方法查找顺序。`super()` 就是沿 MRO 链找下一个类。

---

### 关键字/语法

```python
class Child(Parent1, Parent2):    # 多继承
    super().__init__(args)         # 沿 MRO 找父类的 __init__
```

| 函数 | 作用 |
|------|------|
| `super()` | 按 MRO 顺序返回父类代理 |
| `isinstance(obj, cls)` | obj 是 cls（或其子类）的实例吗？ |
| `issubclass(cls, parent)` | cls 是 parent 的子类吗？ |

---

### 案例

**案例1：基础继承——super() 的正确用法**

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return f"{self.name} 发出声音"

class Cat(Animal):
    def __init__(self, name, breed):
        super().__init__(name)     # 调用父类 __init__
        self.breed = breed
    def speak(self):
        return f"{super().speak()}——喵喵！"

cat = Cat("小花", "英短")
print(cat.speak())  # 小花 发出声音——喵喵！
```

**案例2：多继承 MRO——理解 super() 的调用链**

```python
class A:
    def say(self): print("A")

class B(A):
    def say(self): print("B"); super().say()

class C(A):
    def say(self): print("C"); super().say()

class D(B, C):
    def say(self): print("D"); super().say()

print(D.__mro__)  # D → B → C → A → object
D().say()         # D → B → C → A（super() 沿 MRO 链调用）
```

**案例3（工业级）：Mixin——多继承正确用法（每个 Mixin 只做一件事）**

```python
import json, time

class JSONMixin:
    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

class TimestampMixin:
    def save(self):
        self.updated_at = time.time()
        print(f"保存于 {self.updated_at}")

class BlogPost(JSONMixin, TimestampMixin):   # 自由组合功能
    def __init__(self, title, content):
        self.title = title; self.content = content

post = BlogPost("Python 入门", "...")
post.save(); print(post.to_json())
```

---

## 10.5 多态——同一个接口，不同实现

### 理论：不关心你是谁，只关心你会什么

**鸭子类型**："如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子。"不检查类型，只检查有没有对应的方法。

**ABC（抽象基类）**：当你需要**强制**子类实现某些方法时，用 ABC + `@abstractmethod`。

---

### 案例

**案例1：鸭子类型——代码不依赖具体类型**

```python
class Dog:    def speak(self): return "汪汪"
class Cat:    def speak(self): return "喵喵"

def make_sound(animal):
    return animal.speak()     # 不检查类型，只关心有没有 speak()

print(make_sound(Dog()))      # 汪汪
print(make_sound(Cat()))      # 喵喵
```

**案例2：ABC——强制子类实现特定方法**

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount): ...

class WeChatPay(PaymentProcessor):
    def pay(self, amount): print(f"微信支付 ¥{amount}")

# PaymentProcessor()  # TypeError —— 不能实例化抽象类
```

**案例3（工业级）：策略模式——用多态消除 if-elif**

```python
class DiscountStrategy:
    def apply(self, price): return price    # 默认：原价

class PercentOff(DiscountStrategy):
    def __init__(self, pct): self.pct = pct
    def apply(self, price): return price * (1 - self.pct/100)

strategies = {"原价": DiscountStrategy(), "八折": PercentOff(20)}
def checkout(price, name):
    return strategies[name].apply(price)

print(checkout(200, "八折"))  # 160.0 —— 新增策略只需加一行，不改原代码
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| `class` | 定义类 |
| `__init__` | 构造方法 |
| `self` | 自动指向调用方法的实例 |
| `@classmethod` | 类方法，第一个参数是 cls |
| `@staticmethod` | 静态方法，不需要 self/cls |
| `_x` / `__x` | 约定保护 / 名称改写 |
| `@property` | 方法变属性（getter/setter） |
| `@dataclass` | 自动生成 __init__/__repr__/__eq__ |
| 魔术方法 | `__str__`, `__repr__`, `__eq__`, `__len__`, `__getitem__` 等 |
| `__new__` vs `__init__` | __new__ 创建对象，__init__ 初始化 |
| `__slots__` | 限制属性，节省内存 |
| 继承 | `class C(P):` + `super()` |
| MRO | 多继承方法查找顺序 |
| Mixin | 每个类只做一件事，多继承组合 |
| 鸭子类型 | 不查类型，只看有没有方法 |
| ABC | 抽象基类，强制子类实现 |
