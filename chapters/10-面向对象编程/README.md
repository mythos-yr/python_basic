# 第十章：面向对象编程 (OOP)

---

## 10.1 类和对象——把"东西"抽象成代码

### 理论：为什么需要面向对象？

当你的代码里出现了**一组函数操作同一组数据**时，就是该用类的时候了。

**类比**：不是面向对象的写法，就像把所有工具散落在地上，谁都能拿，容易乱。面向对象是把相关的数据和操作**打包**在一起，像一个工具箱——打开箱子就知道里面有什么工具（方法）和零件（属性）。

**核心概念**：

| 概念 | 含义 | 类比 |
|------|------|------|
| 类 (class) | 创建对象的"模板" | 汽车设计图 |
| 对象/实例 | 按照模板造出来的具体东西 | 你开的那辆具体的车 |
| 属性 (attribute) | 对象拥有的数据 | 颜色、速度、油量 |
| 方法 (method) | 对象能做什么 | 加速、刹车、鸣笛 |

---

### 关键字/语法

```python
class 类名:
    """文档字符串"""

    类属性 = 值               # 所有实例共享

    def __init__(self, 参数):
        self.实例属性 = 参数    # 每个实例独立的属性

    def 方法(self, 参数):
        # self 指向调用此方法的实例
        pass
```

| 关键字 | 作用 |
|--------|------|
| `class` | 定义一个类 |
| `__init__` | 构造方法，创建对象时自动调用 |
| `self` | 代表**调用方法的那个实例**（Python 自动传入） |

**`self` 的本质**：`obj.method(arg)` 等价于 `ClassName.method(obj, arg)`。Python 把 `.` 前面的对象自动传给方法的第一个参数。

---

### 案例

**案例1：基础类的定义和使用**

```python
class Dog:
    species = "Canis familiaris"   # 类属性：所有狗共享

    def __init__(self, name, age):
        self.name = name            # 实例属性：每条狗不同
        self.age = age

    def bark(self):
        return f"{self.name}: 汪汪！"

d1 = Dog("旺财", 3)
d2 = Dog("来福", 5)

print(d1.bark())         # 旺财: 汪汪！
print(d2.name)           # 来福
print(d1.species)        # Canis familiaris (类属性，共享的)
```

**案例2：类属性 vs 实例属性——可变类属性的陷阱**

```python
class Team:
    members = []          # ❌ 类属性，所有实例共享！

    def __init__(self, name):
        self.name = name

a = Team("A队")
b = Team("B队")
a.members.append("张三")  # 看起来只改了 a
print(b.members)           # ['张三'] —— b 也被影响了！

# ✅ 正确做法：在 __init__ 中初始化实例属性
class TeamFixed:
    def __init__(self, name):
        self.name = name
        self.members = []  # 每个实例独立的列表
```

**案例3：@dataclass——一行装饰器替代所有样板代码**

```python
from dataclasses import dataclass, field
from typing import List

# ❌ 传统写法：__init__, __repr__, __eq__ 全要手写

# ✅ @dataclass：自动生成！只用声明字段
@dataclass
class User:
    name: str
    age: int
    email: str = ""
    tags: List[str] = field(default_factory=list)  # 可变默认值必须这样写

user = User("Alice", 30, "a@example.com")
print(user)                 # User(name='Alice', age=30, email='a@example.com')
print(user == User("Alice", 30))  # True
```

---

## 10.2 封装——控制谁能访问什么

### 理论：Python 靠约定而非强制

Python 没有 Java/C++ 那样的 private/public 关键字。它靠**命名约定**：

| 写法 | 含义 | 实际效果 |
|------|------|----------|
| `name` | 公开属性 | 随便访问 |
| `_name` | 约定"受保护的" | 不强制，IDE 提示你不该用 |
| `__name` | 名称改写 (name mangling) | 变成 `_ClassName__name`，不真隐藏但防止子类意外覆盖 |

---

### 关键字/语法

```python
@property       # 把方法变成"属性"的读取方式（getter）
@xxx.setter     # 定义属性的设置逻辑（setter），可加校验
@xxx.deleter    # 定义属性的删除逻辑（deleter）
```

**property 的作用**：让外部像访问普通属性一样访问方法，同时内部保留校验逻辑。从 `obj.get_value()` 变成 `obj.value`。

---

### 案例

**案例1：下划线约定**

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner           # 公开
        self._balance = balance      # 约定：内部属性，别直接改
        self.__pin = "1234"         # 名称改写

acc = BankAccount("Alice", 1000)
print(acc._balance)                  # 能访问，但 IDE 会警告
# print(acc.__pin)                   # AttributeError!
print(acc._BankAccount__pin)         # "1234" —— 改写的名字还是能访问
```

**案例2：property——让属性带校验**

```python
class Temperature:
    def __init__(self, celsius=0):
        self._celsius = celsius

    @property
    def celsius(self):
        """读取——像访问属性一样"""
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        """设置——带校验"""
        if value < -273.15:
            raise ValueError("低于绝对零度！")
        self._celsius = value

    @property
    def fahrenheit(self):
        """华氏温度——只读（无 setter）"""
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.celsius)       # 25 —— 不需要 t.celsius()
t.celsius = 30          # 调用 setter 校验
# t.fahrenheit = 90     # AttributeError —— 只读！
```

**案例3（工业级）：描述符——可复用的字段校验**

```python
class ValidatedField:
    """可复用的字段验证器——Django ORM 的字段就是这样做出来的"""

    def __init__(self, field_type):
        self.field_type = field_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        if not isinstance(value, self.field_type):
            raise TypeError(f"需要 {self.field_type.__name__}")
        setattr(obj, self.name, value)

class User:
    name = ValidatedField(str)
    age = ValidatedField(int)

    def __init__(self, name, age):
        self.name = name    # 触发描述符的 __set__
        self.age = age

# user = User("Alice", "三十")  # TypeError: 需要 int
```

---

## 10.3 继承——利用已有的，扩展自己的

### 理论：is-a 关系用继承，has-a 关系用组合

如果 B 是 A 的一种（狗是动物的一种），用**继承**。如果 B 包含 A（汽车包含引擎），用**组合**。

**MRO（方法解析顺序）**：多继承时，Python 用 C3 线性化算法决定先找哪个父类。`super()` 就是按 MRO 顺序找下一个类。

---

### 关键字/语法

```python
class Child(Parent):
    super().__init__(args)      # 调用父类的 __init__
    super().method()             # 调用父类的方法
```

| 关键字 | 作用 |
|--------|------|
| `class C(P)` | C 继承 P |
| `super()` | 按 MRO 顺序访问父类方法 |
| `isinstance(obj, cls)` | obj 是 cls 或其子类的实例吗？ |
| `issubclass(cls, parent)` | cls 是 parent 的子类吗？ |

---

### 案例

**案例1：基础继承与 super()**

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} 发出声音"

class Cat(Animal):
    def __init__(self, name, breed):
        super().__init__(name)     # 调用父类的 __init__
        self.breed = breed

    def speak(self):
        parent = super().speak()   # 调用父类的 speak
        return f"{parent}——喵喵！"

cat = Cat("小花", "英短")
print(cat.speak())  # 小花 发出声音——喵喵！
```

**案例2：用 MRO 理解 super() 的顺序**

```python
class A:
    def say(self):
        print("A")

class B(A):
    def say(self):
        print("B")
        super().say()

class C(A):
    def say(self):
        print("C")
        super().say()

class D(B, C):
    def say(self):
        print("D")
        super().say()

print(D.__mro__)
# D → B → C → A → object
D().say()   # D → B → C → A
```

**案例3（工业级）：Mixin 多继承的正确用法**

```python
import json, time

# 每个 Mixin 只做一件事
class JSONMixin:
    """混入 JSON 序列化能力"""
    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)

class TimestampMixin:
    """混入时间戳"""
    def save(self):
        self.updated_at = time.time()
        print(f"保存于 {self.updated_at}")

# 业务类——通过多继承自由组合功能
class BlogPost(JSONMixin, TimestampMixin):
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.created_at = time.time()

post = BlogPost("Python 入门", "Mixin 模式...")
post.save()
print(post.to_json())
```

---

## 10.4 多态——同一个接口，不同的实现

### 理论：不关心你是谁，只关心你会什么

**鸭子类型**（Python 的核心哲学）："如果它走起来像鸭子，叫起来像鸭子，那它就是鸭子"。不检查类型，只检查有没有对应的方法。

---

### 案例

**案例1：鸭子类型——不依赖继承的多态**

```python
class Dog:
    def speak(self):
        return "汪汪"

class Cat:
    def speak(self):
        return "喵喵"

class Duck:
    def speak(self):
        return "嘎嘎"

# 这个函数不关心你是什么类型，只关心你有没有 speak()
def make_sound(animal):
    return animal.speak()

print(make_sound(Dog()))   # 汪汪
print(make_sound(Cat()))   # 喵喵
print(make_sound(Duck()))  # 嘎嘎
```

**案例2：抽象基类（ABC）——断言"必须实现"**

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount):
        """子类必须实现此方法"""
        ...

class WeChatPay(PaymentProcessor):
    def pay(self, amount):
        print(f"微信支付 ¥{amount}")

class AliPay(PaymentProcessor):
    def pay(self, amount):
        print(f"支付宝支付 ¥{amount}")

# processor = PaymentProcessor()  # TypeError! 不能实例化抽象类
```

**案例3（工业级）：策略模式——消除 if-elif**

```python
class DiscountStrategy:
    def apply(self, price): ...

class NoDiscount(DiscountStrategy):
    def apply(self, price):
        return price

class PercentOff(DiscountStrategy):
    def __init__(self, percent):
        self.percent = percent
    def apply(self, price):
        return price * (1 - self.percent / 100)

# 策略字典替代 if-elif
strategies = {
    "原价": NoDiscount(),
    "八折": PercentOff(20),
    "半价": PercentOff(50),
}

def checkout(price, strategy_name):
    return strategies[strategy_name].apply(price)

print(checkout(200, "八折"))  # 160.0
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| `class` | 定义类 |
| `__init__` | 构造方法，`obj = Cls(args)` 时调用 |
| `self` | 自动指向调用方法的实例 |
| `_x` | 约定"内部使用" |
| `__x` | 名称改写 `_ClassName__x` |
| `@property` | 方法变属性（getter/setter） |
| `@dataclass` | 自动生成样板代码 |
| `继承` | `class C(P):`，`super()` 调父类 |
| MRO | 多继承方法查找顺序 |
| 鸭子类型 | 不检查类型，只关心有没有方法 |
| ABC | 抽象基类，子类必须实现抽象方法 |
| Mixin | 一个类只做一件事，多继承组合 |
