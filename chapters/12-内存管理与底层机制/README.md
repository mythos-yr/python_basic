# 第十二章：内存管理与底层机制

---

## 12.1 对象与引用

### 知识点：一切都是对象

**案例1：函数和类本身也是对象**

```python
# 函数是一等对象 —— 可以赋值给变量、作为参数传递
def greet(name):
    return f"Hello, {name}!"

# 赋值给变量
say_hello = greet
print(say_hello("Alice"))  # Hello, Alice!

# 函数作为参数
def apply(func, value):
    return func(value)

print(apply(str.upper, "hello"))  # HELLO

# 函数作为返回值
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply  # 返回函数对象

double = make_multiplier(2)
print(double(10))  # 20

# 类本身也是对象！
print(type(greet))     # <class 'function'>
print(type(int))       # <class 'type'>   —— 类也是 type 的实例！
```

**案例2：`is` vs `==` 的底层差异**

```python
# == 比较值是否相等（调用 __eq__）
# is 比较是否是同一个对象（比较 id）

a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(f"a == b: {a == b}")    # True  — 值相同
print(f"a is b: {a is b}")    # False — 不同对象
print(f"a is c: {a is c}")    # True  — 同一个对象

# 整数的特殊行为（小整数缓存池）
x = 256
y = 256
print(f"256 is 256: {x is y}")  # True  — 在缓存池中

x = 257
y = 257
print(f"257 is 257: {x is y}")  # 可能 False！（取决于实现）

# 永远用 is 和 None 比较
result = None
if result is None:          # ✅ 正确
    print("没有结果")

# if result == None:        # ❌ 错误（== 可以被重载）
```

**案例3：工业级 —— 享元模式（减少对象创建）**

```python
from typing import Dict

class ColorPool:
    """
    颜色对象池（享元模式）。
    相同 RGB 值的颜色只创建一个对象，所有地方共享。
    适用于需要大量创建相同颜色对象的图形渲染场景。
    """

    _pool: Dict[tuple, "Color"] = {}

    def __new__(cls, r: int, g: int, b: int):
        """控制对象创建——相同参数返回同一个对象"""
        key = (r, g, b)
        if key not in cls._pool:
            instance = super().__new__(cls)
            instance._r, instance._g, instance._b = r, g, b
            cls._pool[key] = instance
            print(f"  创建新颜色: RGB({r},{g},{b})")
        return cls._pool[key]

    def __init__(self, r, g, b):
        pass   # 初始化在 __new__ 中完成，避免重复初始化

    @classmethod
    def pool_size(cls) -> int:
        return len(cls._pool)


# 创建大量"相同"颜色
colors = []
for _ in range(10):
    colors.append(ColorPool(255, 0, 0))    # 红色 —— 只创建一次
    colors.append(ColorPool(0, 255, 0))    # 绿色 —— 只创建一次

print(f"对象池大小: {ColorPool.pool_size()}")  # 2
print(f"所有红色是同一对象: {all(c is colors[0] for c in colors[::2])}")  # True
```

---

## 12.2 可变与不可变

**案例1：`+=` 对可变和不可变对象的差异**

```python
# 不可变对象：+= 创建新对象
a = (1, 2, 3)
print(f"元组 += 前 id: {id(a)}")
a += (4, 5)           # 创建了新元组！
print(f"元组 += 后 id: {id(a)}")   # id 变了
print(a)              # (1, 2, 3, 4, 5)

# 可变对象：+= 原地修改
b = [1, 2, 3]
print(f"列表 += 前 id: {id(b)}")
b += [4, 5]           # 就地扩展（等价于 extend）
print(f"列表 += 后 id: {id(b)}")   # id 不变！
print(b)              # [1, 2, 3, 4, 5]

# 经典陷阱：元组中的列表
t = (1, 2, [3, 4])
# t[2] += [5, 6]     # 会报错？还是会成功？
try:
    t[2] += [5, 6]
except Exception as e:
    print(f"异常: {type(e).__name__}: {e}")
    # 奇怪的是：虽然报了错，但列表确实被修改了！
    print(f"t = {t}")  # (1, 2, [3, 4, 5, 6]) —— 列表变了！
```

**案例2：函数调用的"传对象引用"深入理解**

```python
def reassign(lst):
    """重新绑定——不影响外部"""
    lst = [4, 5, 6]        # 创建新列表，lst 重新绑定
    lst.append(7)

def mutate(lst):
    """原地修改——影响外部"""
    lst.append(7)           # 修改传入的对象

my_list = [1, 2, 3]

reassign(my_list)
print(f"reassign 后: {my_list}")  # [1, 2, 3] —— 不变

mutate(my_list)
print(f"mutate 后: {my_list}")    # [1, 2, 3, 7] —— 变了！

# 核心理解：
# - 重新赋值（=）：只是换个标签
# - 原地修改（.append(), [0]=x）：修改的是同一个对象
```

**案例3：工业级 —— 不可变配置对象的实现**

```python
from typing import Any, Dict

class FrozenDict:
    """
    不可变字典（只读配置）。
    类似 frozenset 之于 set，确保配置在运行时不会被意外修改。
    """

    def __init__(self, data: Dict[str, Any]):
        # 深拷贝并转为不可变形式
        object.__setattr__(self, "_data", self._freeze_value(data))
        object.__setattr__(self, "_hash", None)

    def _freeze_value(self, value):
        """递归冻结嵌套结构"""
        if isinstance(value, dict):
            return FrozenDict(value)
        elif isinstance(value, list):
            return tuple(self._freeze_value(v) for v in value)
        elif isinstance(value, set):
            return frozenset(self._freeze_value(v) for v in value)
        return value

    def __getattr__(self, key):
        # 支持点号访问: config.db.host
        return self[key]

    def __getitem__(self, key):
        return self._data[key]

    def __contains__(self, key):
        return key in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"FrozenDict({self._data})"

    def __setattr__(self, key, value):
        raise TypeError("FrozenDict 是只读的，不允许修改")

    def __delattr__(self, key):
        raise TypeError("FrozenDict 是只读的，不允许删除")

    def __hash__(self):
        if self._hash is None:
            object.__setattr__(self, "_hash", hash(tuple(sorted(self._data.items()))))
        return self._hash


# 使用
config = FrozenDict({
    "db": {
        "host": "localhost",
        "port": 5432,
    },
    "cache": {
        "servers": ["redis1:6379", "redis2:6379"],
    },
})

print(f"DB主机: {config.db.host}")      # localhost  ← 点号访问
print(f"缓存服务器: {config['cache']['servers']}")

# config.db.host = "newhost"  # TypeError! —— 不可修改
```

---

## 12.3 垃圾回收机制

**案例1：引用计数——Python 的主要内存管理方式**

```python
import sys

# 每个对象都有一个引用计数
a = []                # 引用计数 = 1（a 引用它）
print(f"1个引用: {sys.getrefcount(a) - 1}")   # -1 是因为 getrefcount 本身增加了一个临时引用

b = a                 # 引用计数 = 2（a 和 b 都引用）
print(f"2个引用: {sys.getrefcount(a) - 1}")

c = a                 # 引用计数 = 3
del b                 # 引用计数 = 2
del c                 # 引用计数 = 1

# 当引用计数降到 0 时，对象立即被回收（CPython）
del a                 # 对象被回收
# print(a)            # NameError!
```

**案例2：循环引用——为什么需要 GC**

```python
import gc

# 循环引用：两个对象互相引用，但外部无法访问
class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None

# 创建循环引用
a = Node("A")
b = Node("B")
a.ref = b
b.ref = a

# 即使删除外部引用，两个对象依然互相引用
del a
del b
# 引用计数不会降到 0！需要 GC 的循环检测来回收

# 手动触发垃圾回收
gc.collect()
print(f"回收后对象数: {len(gc.get_objects())}")

# 在开发中，用弱引用（weakref）来避免循环引用
import weakref

class NodeGood:
    def __init__(self, name):
        self.name = name
        self._ref = None

    @property
    def ref(self):
        if self._ref is not None:
            return self._ref()
        return None

    @ref.setter
    def ref(self, node):
        self._ref = weakref.ref(node)  # 弱引用：不增加引用计数
```

**案例3：工业级 —— 内存泄漏排查工具**

```python
import gc
import sys
from typing import List, Dict
import tracemalloc

class MemoryProfiler:
    """
    内存分析工具。
    用于排查生产环境中的内存泄漏问题。
    """

    @staticmethod
    def count_by_type():
        """按类型统计当前内存中的对象数量"""
        counts: Dict[str, int] = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            counts[obj_type] = counts.get(obj_type, 0) + 1

        # 按数量降序排列
        for obj_type, count in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{obj_type:>25}: {count:>8}")

    @staticmethod
    def get_size(obj, seen=None):
        """递归计算对象的内存占用（近似）"""
        if seen is None:
            seen = set()

        obj_id = id(obj)
        if obj_id in seen:
            return 0
        seen.add(obj_id)

        size = sys.getsizeof(obj)

        if isinstance(obj, dict):
            size += sum(MemoryProfiler.get_size(k, seen) + MemoryProfiler.get_size(v, seen)
                       for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set, frozenset)):
            size += sum(MemoryProfiler.get_size(i, seen) for i in obj)

        return size

    @staticmethod
    def track_top_memory(n: int = 5):
        """追踪占用内存最多的前 N 个对象"""
        # 启动内存追踪
        tracemalloc.start()

        # 取当前快照
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics("lineno")

        print(f"\n内存占用 Top {n}:")
        for stat in top_stats[:n]:
            print(f"  {stat.size / 1024:.1f} KB: {stat}")
            for line in stat.traceback.format()[:3]:
                print(f"    {line}")


# 使用
# profiler = MemoryProfiler()
# profiler.count_by_type()
# profiler.track_top_memory()
```

---

## 12.4 深浅拷贝（回顾与实践）

**案例1：`=`、浅拷贝、深拷贝的可视化验证**

```python
import copy

# 原始数据结构
original = {
    "name": "Alice",
    "scores": [85, 92, 78],
    "address": {"city": "Beijing", "district": "Haidian"}
}

def show_all(original, shallow, deep):
    """展示三种变量与原始对象的关系"""
    # 检查顶层字典是否是同一个对象
    print(f"original is shallow: {original is shallow}")   # False
    print(f"original is deep: {original is deep}")         # False

    # 检查嵌套的可变对象是否共享
    print(f"original['scores'] is shallow['scores']: {original['scores'] is shallow['scores']}")  # True！
    print(f"original['scores'] is deep['scores']: {original['scores'] is deep['scores']}")        # False

    print(f"original['address'] is shallow['address']: {original['address'] is shallow['address']}")  # True！
    print(f"original['address'] is deep['address']: {original['address'] is deep['address']}")        # False

shallow = copy.copy(original)
deep = copy.deepcopy(original)
show_all(original, shallow, deep)
```

**案例2：子类重写 __copy__ 和 __deepcopy__**

```python
import copy

class ManagedResource:
    """管理的资源——被复制时需要特殊处理"""

    def __init__(self, data):
        self.data = data
        self._connection = id(self)  # 模拟外部连接

    def __copy__(self):
        """浅拷贝时：共享连接，复制数据"""
        print("调用 __copy__")
        new = type(self).__new__(type(self))
        new.data = self.data[:]  # 浅拷贝数据
        new._connection = self._connection  # 共享同一个连接
        return new

    def __deepcopy__(self, memo):
        """深拷贝时：创建新连接，深拷贝数据"""
        print("调用 __deepcopy__")
        new = type(self).__new__(type(self))
        new.data = copy.deepcopy(self.data, memo)
        new._connection = id(new)  # 创建全新的连接
        return new

    def __repr__(self):
        return f"ManagedResource(data={self.data}, conn={self._connection})"


r1 = ManagedResource([1, 2, [3, 4]])
r2 = copy.copy(r1)
r3 = copy.deepcopy(r1)

print(f"原始:     {r1}")
print(f"浅拷贝:   {r2}")
print(f"深拷贝:   {r3}")
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| 引用计数 | CPython 的主要 GC 方式，引用为 0 立即回收 |
| 循环引用 | 两个对象互相引用，引用计数永远 > 0，需要分代 GC |
| 小整数缓存 | -5 ~ 256 的 int 对象被缓存复用 |
| 字符串驻留 | 短字符串可能被 intern，相同字符串共享同一对象 |
| `is` vs `==` | is 比较 id（同一对象），== 比较值（调用 __eq__） |
| 可变 vs 不可变 | 可变对象可原地修改，不可变对象只能创建新的 |
| 浅拷贝 | 复制外层，内部元素共享引用 |
| 深拷贝 | 递归复制所有层级，完全独立 |
