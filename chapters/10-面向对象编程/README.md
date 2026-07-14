# 第十章：面向对象编程 (OOP)

---

## 10.1 类与对象基础

### 知识点：class、__init__、self

**案例1：理解 self —— 谁调用，self 就是谁**

```python
class Dog:
    """狗类：演示 self 的本质"""

    # 类属性：所有实例共享
    species = "Canis familiaris"

    def __init__(self, name: str, age: int):
        # 实例属性：每个实例独立拥有
        self.name = name
        self.age = age
        print(f"创建了 {self.name}，self 的 id = {id(self)}")

    def bark(self):
        """self 指向调用这个方法的实例"""
        print(f"{self.name} (id={id(self)}) 在叫: 汪汪！")


# self 是谁？就是调用方法的那个对象
dog1 = Dog("旺财", 3)
dog2 = Dog("来福", 5)

dog1.bark()    # self = dog1
dog2.bark()    # self = dog2

# Dog.bark(dog1)  # 等价于 dog1.bark()——方法的本质是函数
```

**案例2：类属性 vs 实例属性 —— 经典陷阱**

```python
class Team:
    # 类属性：所有实例共享一个列表！
    members: list = []

    def __init__(self, name: str):
        self.name = name   # 实例属性

# ❌ 陷阱：类属性是可变的
team_a = Team("A队")
team_b = Team("B队")

team_a.members.append("张三")
print(f"A队: {team_a.members}")  # ['张三']
print(f"B队: {team_b.members}")  # ['张三'] ← 也被影响了！

# 为什么会这样？
# team_a.members 实际上访问的是 Team.members（类属性）
# 因为 team_a 实例上没有 members 属性，所以沿着 MRO 找到了类的

# ✅ 正确做法：在 __init__ 中初始化实例属性
class TeamFixed:
    def __init__(self, name: str):
        self.name = name
        self.members: list = []   # 每个实例独立的列表！
```

**案例3：工业级 —— @dataclass 简化数据类**

```python
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime

# ❌ 传统写法：几十行样板代码
class UserOld:
    def __init__(self, name, age, email=None):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"User(name={self.name!r}, age={self.age!r})"

    def __eq__(self, other):
        if not isinstance(other, UserOld):
            return False
        return self.name == other.name and self.age == other.age

# ✅ @dataclass：一行装饰器替代几十行样板代码
@dataclass
class User:
    """用户数据类——自动生成 __init__, __repr__, __eq__"""
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = field(default_factory=list)  # 注意：可变默认值用 default_factory
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def is_adult(self) -> bool:
        return self.age >= 18


# 自动生成的方法
user1 = User("Alice", 30, email="alice@example.com")
user2 = User("Alice", 30, email="alice@example.com")

print(user1)                      # User(name='Alice', age=30, ...)
print(user1 == user2)             # True（自动生成的 __eq__）
print(asdict(user1))              # 转为字典

# field() 的高级用法
@dataclass
class APIConfig:
    host: str
    port: int = 443
    timeout: float = field(default=30.0, metadata={"unit": "seconds"})
    _cache: dict = field(default_factory=dict, repr=False)  # repr=False 不显示

config = APIConfig("api.example.com")
print(config)  # APIConfig(host='api.example.com', port=443, timeout=30.0)
```

---

## 10.2 访问控制与 property

### 知识点：下划线约定与 property 装饰器

**案例1：单下划线、双下划线的区别**

```python
class AccessDemo:
    def __init__(self):
        self.public = "公开属性"        # 公开：随便访问
        self._protected = "约定保护"    # _ 开头：约定为"内部使用"
        self.__private = "名称改写"     # __ 开头：触发 name mangling

obj = AccessDemo()
print(obj.public)              # 公开属性
print(obj._protected)          # 约定保护（Python 不强制，但 IDE 会警告）

# print(obj.__private)         # AttributeError!
# 但实际上可以通过改写后的名字访问：
print(obj._AccessDemo__private)  # 名称改写（不推荐！）
```

**案例2：property —— 让方法像属性一样访问**

```python
class Temperature:
    """温度类：用 property 控制属性的读写"""

    def __init__(self, celsius: float = 0):
        self._celsius = celsius   # 内部存储用 _celsius

    @property
    def celsius(self) -> float:
        """读取摄氏温度（像属性一样访问）"""
        return self._celsius

    @celsius.setter
    def celsius(self, value: float):
        """设置摄氏温度（带校验）"""
        if value < -273.15:
            raise ValueError(f"温度不能低于绝对零度（-273.15°C），得到: {value}")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        """华氏温度（只读属性，没有 setter）"""
        return self._celsius * 9 / 5 + 32


temp = Temperature(25)
print(temp.celsius)       # 25    — 像属性一样用，不需要 temp.celsius()
print(temp.fahrenheit)    # 77.0  — 只读属性

temp.celsius = 100        # 调用 setter
# temp.celsius = -500     # ValueError!

# temp.fahrenheit = 90    # AttributeError! —— 没有 setter
```

**案例3：工业级 —— ORM 风格的字段验证**

```python
from dataclasses import dataclass, field
from typing import Any, Optional
import re

class ValidatedField:
    """
    带验证的描述符字段。
    像 Django ORM 的字段一样，自动校验类型和约束。
    """

    def __init__(self, field_type, required=True, min_length=None, max_length=None, pattern=None):
        self.field_type = field_type
        self.required = required
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.name = None  # 在 __set_name__ 中设置

    def __set_name__(self, owner, name):
        self.name = name
        self._attr_name = f"_{name}"

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return getattr(obj, self._attr_name, None)

    def __set__(self, obj, value):
        # 类型检查
        if value is not None and not isinstance(value, self.field_type):
            actual_type = type(value).__name__
            expected = self.field_type.__name__
            raise TypeError(f"{self.name}: 需要 {expected}，得到 {actual_type}")

        # 必填检查
        if self.required and (value is None or value == ""):
            raise ValueError(f"{self.name} 是必填项")

        # 长度检查
        if self.min_length and isinstance(value, str) and len(value) < self.min_length:
            raise ValueError(f"{self.name}: 最小长度 {self.min_length}")

        if self.max_length and isinstance(value, str) and len(value) > self.max_length:
            raise ValueError(f"{self.name}: 最大长度 {self.max_length}")

        # 正则检查
        if self.pattern and isinstance(value, str) and not self.pattern.match(value):
            raise ValueError(f"{self.name}: 不匹配模式 {self.pattern.pattern}")

        setattr(obj, self._attr_name, value)


# 使用描述符的模型类
class UserModel:
    """类似 Django Model 的用户模型"""

    name = ValidatedField(str, min_length=2, max_length=50)
    email = ValidatedField(str, required=True, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age = ValidatedField(int, required=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        # 检查必填项
        for attr_name in dir(type(self)):
            attr = getattr(type(self), attr_name)
            if isinstance(attr, ValidatedField) and attr.required:
                if getattr(self, attr_name, None) is None:
                    raise ValueError(f"{attr_name} 是必填项")


# 使用
try:
    user = UserModel(name="A", email="bad_email", age="not_int")
except (TypeError, ValueError) as e:
    print(f"校验失败: {e}")

user = UserModel(name="Alice", email="alice@example.com", age=30)
print(f"创建成功: {user.name}, {user.email}, {user.age}")
```

---

## 10.3 魔术方法 (Dunder Methods)

### 知识点：让自定义对象像内置类型一样运作

**案例1：__str__ vs __repr__**

```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        """给开发者看的——应该能"重现"这个对象"""
        return f"Point({self.x}, {self.y})"

    def __str__(self):
        """给用户看的——应该可读性强"""
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __abs__(self):
        """点到原点的距离"""
        return (self.x ** 2 + self.y ** 2) ** 0.5


p1 = Point(3, 4)
p2 = Point(1, 2)

print(p1)                 # (3, 4) — 调用 __str__
print(repr(p1))           # Point(3, 4) — 调用 __repr__
print(p1 == p2)           # False — 调用 __eq__
print(p1 + p2)            # (4, 6) — 调用 __add__
print(abs(p1))            # 5.0 — 调用 __abs__
```

**案例2：模拟容器——__getitem__、__setitem__、__len__**

```python
class HistoryList:
    """带历史记录功能的列表"""

    def __init__(self):
        self._data = []
        self._history = []   # 操作历史

    def append(self, item):
        self._data.append(item)
        self._history.append(f"添加: {item}")

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        old = self._data[index]
        self._data[index] = value
        self._history.append(f"修改: [{index}] {old} → {value}")

    def __len__(self):
        return len(self._data)

    def __contains__(self, item):
        return item in self._data

    def __iter__(self):
        return iter(self._data)

    def __repr__(self):
        return f"HistoryList({self._data})"

    def get_history(self):
        return self._history


hl = HistoryList()
hl.append("A")
hl.append("B")
hl.append("C")

print(len(hl))            # 3 —— __len__
print(hl[1])              # B —— __getitem__
print("B" in hl)          # True —— __contains__
print([x for x in hl])    # ['A', 'B', 'C'] —— __iter__

hl[1] = "X"               # __setitem__
print(hl.get_history())
# ['添加: A', '添加: B', '添加: C', '修改: [1] B → X']
```

**案例3：工业级 —— 惰性属性缓存（__getattr__ 实现懒加载）**

```python
import time
from typing import Dict, Callable

class LazyModel:
    """
    惰性加载模型。
    昂贵的属性（数据库查询、网络请求）直到被访问时才计算，
    计算后被缓存，避免重复计算。
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._cache: Dict[str, object] = {}
        self._loaders: Dict[str, Callable] = {
            "profile": self._load_profile,
            "orders": self._load_orders,
            "recommendations": self._load_recommendations,
        }

    # -------- 惰性加载器（模拟昂贵操作）--------
    def _load_profile(self):
        print(f"  [昂贵操作] 从数据库加载用户 {self.user_id} 的资料...")
        time.sleep(0.5)
        return {"name": "Alice", "age": 30, "city": "Beijing"}

    def _load_orders(self):
        print(f"  [昂贵操作] 从数据库加载用户 {self.user_id} 的订单...")
        time.sleep(0.8)
        return [{"id": 101, "amount": 99.9}, {"id": 102, "amount": 199.9}]

    def _load_recommendations(self):
        print(f"  [昂贵操作] 计算用户 {self.user_id} 的推荐...")
        time.sleep(1.0)
        return ["Python入门", "算法导论", "设计模式"]

    # -------- 魔法方法 --------
    def __getattr__(self, name: str):
        """
        访问不存在的属性时才触发！
        注意：如果属性已经存在于实例的 __dict__ 中，__getattr__ 不会被调用。
        """
        if name in self._loaders:
            # 执行加载
            value = self._loaders[name]()
            # 缓存到实例属性（下次访问直接走 __dict__，不再触发 __getattr__）
            setattr(self, name, value)
            return value
        raise AttributeError(f"'{type(self).__name__}' 没有属性 '{name}'")


# 使用
print("创建 LazyModel 对象（尚未加载任何数据）")
user = LazyModel(user_id=42)

print("\n第一次访问 profile（触发加载）:")
print(user.profile)     # 触发 __getattr__ → _load_profile → 缓存

print("\n第二次访问 profile（从缓存读取，不会重新加载）:")
print(user.profile)     # 走 __dict__，不再触发 __getattr__

print("\n第一次访问 orders（触发加载）:")
print(user.orders)
```

---

## 10.4 继承与多态

### 知识点：super() 与 MRO

**案例1：super() 的正确用法**

```python
class Animal:
    def __init__(self, name: str):
        self.name = name
        print(f"Animal.__init__: {self.name}")

    def speak(self):
        return f"{self.name} 发出声音"

class Pet(Animal):
    def __init__(self, name: str, owner: str):
        super().__init__(name)          # ← 调用父类的 __init__
        self.owner = owner
        print(f"Pet.__init__: 主人是 {self.owner}")

    def speak(self):
        parent_result = super().speak()  # ← 调用父类的 speak
        return f"{parent_result}，然后向主人 {self.owner} 撒娇"


cat = Pet("小花", "Alice")
print(cat.speak())
# 输出:
# Animal.__init__: 小花
# Pet.__init__: 主人是 Alice
# 小花 发出声音，然后向主人 Alice 撒娇
```

**案例2：多继承与 MRO**

```python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")
        super().method()

class C(A):
    def method(self):
        print("C.method")
        super().method()

class D(B, C):
    """多继承：B 和 C 都继承 A"""
    def method(self):
        print("D.method")
        super().method()   # super() 按 MRO 顺序找下一个


# MRO: Method Resolution Order（方法解析顺序）
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)

d = D()
d.method()
# D.method
# B.method
# C.method
# A.method
# ← super() 让调用链按 MRO 顺序依次执行！
```

**案例3：工业级 —— Mixin 模式（多继承的正确姿势）**

```python
import json
import time
from typing import Any, Dict

# ===== Mixin 类：每个 Mixin 只负责一个功能 =====

class TimestampMixin:
    """自动添加创建时间和更新时间"""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__init__" not in cls.__dict__:
            # 如果子类没有定义 __init__，添加一个默认的
            original_init = cls.__init__

            def new_init(self, *args, **kwargs):
                self.created_at = time.time()
                self.updated_at = time.time()
                if original_init is not object.__init__:
                    original_init(self, *args, **kwargs)

            cls.__init__ = new_init


class JSONSerializableMixin:
    """让对象可以转为 JSON 字典"""
    def to_dict(self) -> Dict[str, Any]:
        """将实例属性转为字典（排除私有属性和方法）"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                result[key] = value
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent, default=str)


class LoggingMixin:
    """混入日志功能"""
    def log(self, message: str):
        print(f"[{type(self).__name__}] {message}")


# ===== 业务类：通过多重继承组合功能 =====
class BlogPost(TimestampMixin, JSONSerializableMixin, LoggingMixin):
    """博客文章——通过 Mixin 组合了时间戳、JSON 序列化、日志三种功能"""

    def __init__(self, title: str, content: str, author: str):
        self.title = title
        self.content = content
        self.author = author
        # TimestampMixin 需要 created_at 和 updated_at
        if not hasattr(self, "created_at"):
            self.created_at = time.time()
            self.updated_at = time.time()

    def publish(self):
        self.updated_at = time.time()
        self.log(f"发布文章: {self.title}")
        return self.to_json()


# 使用
post = BlogPost("Python 多继承的正确姿势", "Mixin 模式...", "Alice")
json_str = post.publish()
print(json_str)

# 功能都是"混"进去的，BlogPost 本身只定义了核心业务逻辑
```

---

## 10.5 抽象基类与协议

**案例1：抽象基类强制接口实现**

```python
from abc import ABC, abstractmethod

class PaymentProcessor(ABC):
    """支付处理器抽象基类——定义接口契约"""

    @abstractmethod
    def pay(self, amount: float) -> bool:
        """支付——子类必须实现"""
        ...

    @abstractmethod
    def refund(self, transaction_id: str) -> bool:
        """退款——子类必须实现"""
        ...

    def log(self, message: str):
        """非抽象方法——子类可选覆盖"""
        print(f"[{type(self).__name__}] {message}")


class WeChatPay(PaymentProcessor):
    def pay(self, amount: float) -> bool:
        print(f"微信支付: ¥{amount}")
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"微信退款: {transaction_id}")
        return True


class AliPay(PaymentProcessor):
    def pay(self, amount: float) -> bool:
        print(f"支付宝支付: ¥{amount}")
        return True

    def refund(self, transaction_id: str) -> bool:
        print(f"支付宝退款: {transaction_id}")
        return True


# ❌ 不能实例化抽象类
# processor = PaymentProcessor()  # TypeError!

# ✅ 子类必须实现所有抽象方法
wechat = WeChatPay()
wechat.pay(100.0)
```

**案例2：鸭子类型与 Protocol（静态鸭子类型）**

```python
from typing import Protocol, runtime_checkable

# Python 的鸭子类型传统
def make_sound_duck(animal):
    """鸭子类型：不检查类型，只看有没有 speak() 方法"""
    return animal.speak()


class Dog:
    def speak(self):
        return "汪汪"

class Cat:
    def speak(self):
        return "喵喵"

print(make_sound_duck(Dog()))  # 汪汪
print(make_sound_duck(Cat()))  # 喵喵


# Protocol: 静态鸭子类型（类型检查器可以验证）
@runtime_checkable
class Speaker(Protocol):
    def speak(self) -> str:
        ...

# 不需要显式继承 Speaker，只要有 speak() 方法就满足协议
class Duck:
    def speak(self) -> str:
        return "嘎嘎"

print(isinstance(Duck(), Speaker))  # True！即使 Duck 没有继承 Speaker
```

**案例3：工业级 —— 策略模式（多态替代 if-else）**

```python
from typing import Dict, Type
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    """折扣策略抽象基类"""

    @abstractmethod
    def apply(self, price: float) -> float:
        ...

    @abstractmethod
    def description(self) -> str:
        ...


class NoDiscount(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price

    def description(self) -> str:
        return "原价"


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self.percent = percent

    def apply(self, price: float) -> float:
        return price * (1 - self.percent / 100)

    def description(self) -> str:
        return f"{self.percent}% 折扣"


class FixedDiscount(DiscountStrategy):
    def __init__(self, amount: float):
        self.amount = amount

    def apply(self, price: float) -> float:
        return max(0, price - self.amount)

    def description(self) -> str:
        return f"立减 ¥{self.amount}"


class BuyOneGetOne(DiscountStrategy):
    def apply(self, price: float) -> float:
        return price / 2

    def description(self) -> str:
        return "买一赠一"


# 策略注册表（比 if-elif 链更优雅）
class DiscountRegistry:
    _strategies: Dict[str, Type[DiscountStrategy]] = {}

    @classmethod
    def register(cls, name: str, strategy_cls: Type[DiscountStrategy]):
        cls._strategies[name] = strategy_cls

    @classmethod
    def get(cls, name: str, **kwargs) -> DiscountStrategy:
        if name not in cls._strategies:
            raise ValueError(f"未知折扣策略: {name}")
        return cls._strategies[name](**kwargs)


# 注册策略
DiscountRegistry.register("none", NoDiscount)
DiscountRegistry.register("percent", PercentageDiscount)
DiscountRegistry.register("fixed", FixedDiscount)
DiscountRegistry.register("bogo", BuyOneGetOne)


# 结账（无需 if-elif）
def checkout(price: float, discount_name: str, **discount_params):
    strategy = DiscountRegistry.get(discount_name, **discount_params)
    final_price = strategy.apply(price)
    saved = price - final_price
    print(f"原价: ¥{price:.2f}")
    print(f"策略: {strategy.description()}")
    print(f"实付: ¥{final_price:.2f}，省了 ¥{saved:.2f}")


checkout(200, "percent", percent=20)  # 原价200，打8折
checkout(200, "fixed", amount=50)     # 原价200，满减50
checkout(200, "bogo")                 # 原价200，买一赠一
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| `self` | 谁调用方法，self 就指向谁 |
| 类属性 vs 实例属性 | 类属性共享（定义在 class 下），实例属性独立（在 __init__ 中用 self.xxx） |
| `_x` | 约定保护（不强制，但 IDE 警告） |
| `__x` | 名称改写（变成 `_ClassName__x`） |
| `@property` | 让方法像属性一样访问（getter/setter/deleter） |
| `@dataclass` | 自动生成 __init__, __repr__, __eq__ |
| `__str__` vs `__repr__` | str 给用户看，repr 给开发者看 |
| `super()` | 按 MRO 顺序找父类 |
| MRO | 多继承的方法解析顺序（C3 线性化） |
| ABC | 抽象基类，强制子类实现方法 |
| Protocol | 静态鸭子类型（不需要继承，有方法就行） |
| Mixin | 多继承的正确用法（每个 Mixin 只做一件事） |
