# 第四章：内置容器类型 —— 四种核心数据结构

> 这是 Python 中使用频率最高的一章。掌握这四种容器，就掌握了日常开发的 80%。

---

## 4.1 列表 (list)

### 知识点：列表的增删改查

**案例1：增 —— 四种添加方式的区别**

```python
# append: 在末尾追加一个元素（最常用）
fruits = ["apple", "banana"]
fruits.append("orange")
print(fruits)  # ['apple', 'banana', 'orange']

# insert: 在指定位置插入
fruits.insert(1, "grape")
print(fruits)  # ['apple', 'grape', 'banana', 'orange']

# extend: 展开另一个可迭代对象，逐个追加
fruits.extend(["kiwi", "mango"])
print(fruits)  # ['apple', 'grape', 'banana', 'orange', 'kiwi', 'mango']

# ⚠️ extend vs append 的经典区别
nums = [1, 2, 3]
nums.append([4, 5])
print(nums)   # [1, 2, 3, [4, 5]]    ← 整个列表作为一个元素
nums2 = [1, 2, 3]
nums2.extend([4, 5])
print(nums2)  # [1, 2, 3, 4, 5]      ← 逐个展开添加
```

**案例2：删 —— 五种删除方式的区别**

```python
nums = [10, 20, 30, 40, 50, 20]

# pop(): 删除并返回最后一个元素（或指定索引）
last = nums.pop()
print(f"删除了 {last}, 剩余: {nums}")  # 删除了 20, 剩余: [10, 20, 30, 40, 50]

second = nums.pop(1)
print(f"删除了索引1的元素 {second}, 剩余: {nums}")  # 删除了20, 剩余: [10, 30, 40, 50]

# remove(): 按值删除（只删第一个匹配的）
nums2 = [1, 2, 3, 2, 4]
nums2.remove(2)           # 删除第一个 2
print(nums2)               # [1, 3, 2, 4]

# del: 按索引删除（可以删切片）
nums3 = [1, 2, 3, 4, 5]
del nums3[1]               # 删除索引1的元素
print(nums3)                # [1, 3, 4, 5]
del nums3[1:3]             # 删除切片 1:3
print(nums3)                # [1, 5]

# clear(): 清空列表
nums3.clear()
print(nums3)                # []
```

**案例3：工业级 —— 去重并保持原始顺序**

```python
from typing import List, TypeVar, Hashable

T = TypeVar("T", bound=Hashable)

def deduplicate_preserve_order(items: List[T]) -> List[T]:
    """
    列表去重，保持原始顺序（Python 3.7+ dict 保持插入顺序）。
    时间复杂度 O(n)，空间复杂度 O(n)。

    常见场景：日志去重、用户 ID 去重、URL 去重等。
    """
    return list(dict.fromkeys(items))

# 对比：set 去重会丢失顺序
items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
print(f"原始:     {items}")
print(f"set去重:  {list(set(items))}")       # 顺序乱了
print(f"保持顺序: {deduplicate_preserve_order(items)}")  # [3, 1, 4, 5, 9, 2, 6]


# 进阶：按某个字段去重
def deduplicate_by_key(items: List[dict], key: str) -> List[dict]:
    """按字典的某个字段去重，保留第一次出现的记录"""
    seen = set()
    result = []
    for item in items:
        val = item.get(key)
        if val not in seen:
            seen.add(val)
            result.append(item)
    return result

records = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice_Duplicate"},  # 重复的 id
]
print(deduplicate_by_key(records, "id"))
# [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]
```

---

### 知识点：列表的排序

**案例1：sort() vs sorted()**

```python
# sort(): 原地排序，不返回新列表（返回 None）
nums = [3, 1, 4, 1, 5]
result = nums.sort()         # result 是 None！
print(nums)                  # [1, 1, 3, 4, 5] — 原列表被修改

# sorted(): 返回新列表，原列表不变
nums = [3, 1, 4, 1, 5]
new_nums = sorted(nums)
print(nums)                  # [3, 1, 4, 1, 5] — 原列表不变
print(new_nums)              # [1, 1, 3, 4, 5] — 新列表

# 注意：sort() 只能用于列表；sorted() 可用于任何可迭代对象
print(sorted("python"))      # ['h', 'n', 'o', 'p', 't', 'y']
print(sorted({3, 1, 2}))     # [1, 2, 3]
```

**案例2：key 参数的高级用法**

```python
# 按字符串长度排序
words = ["python", "go", "rust", "c", "javascript"]
print(sorted(words, key=len))          # ['c', 'go', 'rust', 'python', 'javascript']

# 按元组的某个元素排序
students = [("Alice", 85), ("Bob", 92), ("Charlie", 78)]
print(sorted(students, key=lambda s: s[1], reverse=True))
# [('Bob', 92), ('Alice', 85), ('Charlie', 78)]

# 多级排序：先按年龄升序，再按姓名降序
people = [("Alice", 25), ("Bob", 30), ("Charlie", 25)]
# 用元组作为 key：Python 逐个元素比较
print(sorted(people, key=lambda p: (p[1], p[0])))
# [('Alice', 25), ('Charlie', 25), ('Bob', 30)]

# 巧用负号实现部分升序、部分降序
data = [("A", 10), ("B", 5), ("C", 10)]
# 第二个字段降序（取负），第一个字段升序
print(sorted(data, key=lambda x: (-x[1], x[0])))
# [('A', 10), ('C', 10), ('B', 5)]
```

**案例3：工业级 —— 自然排序（人读排序）**

```python
import re
from typing import List

def natural_sort_key(text: str):
    """
    自然排序：将字符串中的数字段转为整数进行比较。
    例: ["file2.txt", "file10.txt", "file1.txt"]
    普通排序:  file1.txt, file10.txt, file2.txt （字典序）
    自然排序:  file1.txt, file2.txt, file10.txt（数字按数值大小）
    """
    def convert(part):
        return int(part) if part.isdigit() else part.lower()
    return [convert(part) for part in re.split(r"(\d+)", text)]


filenames = [
    "file10.txt", "file2.txt", "file1.txt",
    "file20.txt", "file3.txt"
]

# 普通排序（不符合人类直觉）
print("普通排序:", sorted(filenames))
# ['file1.txt', 'file10.txt', 'file2.txt', 'file20.txt', 'file3.txt']

# 自然排序
print("自然排序:", sorted(filenames, key=natural_sort_key))
# ['file1.txt', 'file2.txt', 'file3.txt', 'file10.txt', 'file20.txt']


# 实战场景：版本号排序
def sort_versions(versions: List[str]) -> List[str]:
    """对语义化版本号排序"""
    def version_key(v: str):
        # "2.10.3" → (2, 10, 3)
        parts = v.lstrip("v").split(".")
        return tuple(int(p) for p in parts)
    return sorted(versions, key=version_key)

vers = ["v2.1.0", "v1.10.0", "v1.2.3", "v2.0.1"]
print(sort_versions(vers))
# ['v1.2.3', 'v1.10.0', 'v2.0.1', 'v2.1.0']
```

---

### 知识点：列表的深浅拷贝

**案例1：赋值 vs 浅拷贝 vs 深拷贝**

```python
import copy

# 原始数据
original = [1, 2, [10, 20]]

# 1. 赋值（=）：不复制，只是多一个引用
ref = original
print(f"ref is original: {ref is original}")  # True

# 2. 浅拷贝：复制外层，内部元素共享引用
shallow = copy.copy(original)       # 或 original.copy(), original[:]
print(f"shallow is original: {shallow is original}")  # False — 不同对象
print(f"shallow[2] is original[2]: {shallow[2] is original[2]}")  # True — 内层列表共享！

# 3. 深拷贝：递归复制所有层级
deep = copy.deepcopy(original)
print(f"deep is original: {deep is original}")           # False
print(f"deep[2] is original[2]: {deep[2] is original[2]}")  # False — 内层也是独立的！

# 验证
original[2].append(30)
print(f"修改后 shallow[2] = {shallow[2]}")   # [10, 20, 30] — 也变了
print(f"修改后 deep[2] = {deep[2]}")         # [10, 20] — 不受影响
```

**案例2：可视化深浅拷贝**

```python
# 用 id 直观展示内存关系
import copy

def show_memory(obj, name):
    """打印对象及其嵌套元素的 id"""
    print(f"{name}: id={id(obj)}")
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"  [{i}]: id={id(item)}, value={item}")

original = [1, 2, [10, 20]]
shallow = copy.copy(original)
deep = copy.deepcopy(original)

print("=== 原始列表 ===")
show_memory(original, "original")
print("\n=== 浅拷贝 ===")
show_memory(shallow, "shallow")
print("\n=== 深拷贝 ===")
show_memory(deep, "deep")
# 注意观察：浅拷贝和原始列表的内层列表 id 相同！
#          深拷贝的内层列表 id 完全不同！
```

**案例3：工业级 —— 不可变数据的防御性拷贝**

```python
import copy
from typing import Dict, List, Any

class Configuration:
    """
    配置管理器。所有获取的配置都返回深拷贝，
    防止调用方意外修改内部状态。
    """

    def __init__(self, initial_config: Dict[str, Any]):
        # 存储时也做深拷贝，防止外部修改传入的字典
        self._config = copy.deepcopy(initial_config)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（返回深拷贝）"""
        value = self._config.get(key, default)
        return copy.deepcopy(value)  # 防御性拷贝

    def get_all(self) -> Dict[str, Any]:
        """获取全部配置（返回深拷贝）"""
        return copy.deepcopy(self._config)

    def update(self, key: str, value: Any) -> None:
        """更新配置"""
        self._config[key] = copy.deepcopy(value)

    def merge(self, updates: Dict[str, Any]) -> None:
        """合并配置"""
        for k, v in updates.items():
            self._config[k] = copy.deepcopy(v)


# 演示防御性拷贝的必要性
config = Configuration({"db": {"host": "localhost", "port": 5432}})

# 获取配置并尝试修改
db_config = config.get("db")
db_config["host"] = "evil.com"    # 尝试修改...

# 内部配置不受影响
print(config.get("db"))           # {'host': 'localhost', 'port': 5432}
```

---

## 4.2 元组 (tuple)

### 知识点：元组的不可变性与解包

**案例1：元组的基础操作**

```python
# 创建方式
t1 = (1, 2, 3)
t2 = 1, 2, 3           # 括号可以省略
t3 = (1,)              # ⚠️ 单元素元组必须有逗号
t4 = (1)               # 这不是元组！是整数 1

print(type(t1))        # <class 'tuple'>
print(type(t2))        # <class 'tuple'>
print(type(t3))        # <class 'tuple'>
print(type(t4))        # <class 'int'>  ← 注意！

# 不可变意味着不能修改
# t1[0] = 10          # TypeError!
# t1.append(4)        # AttributeError!

# 但 "不可变" 只针对引用，如果元组中包含可变对象...
t = (1, [2, 3], 4)
t[1].append(5)         # ✅ 可以！因为修改的是列表内容，不是元组引用
print(t)               # (1, [2, 3, 5], 4)
```

**案例2：解包的多种姿势**

```python
# 基础解包
a, b, c = (1, 2, 3)
print(f"a={a}, b={b}, c={c}")

# 星号解包（吞掉剩余元素）
first, *middle, last = (1, 2, 3, 4, 5)
print(f"first={first}, middle={middle}, last={last}")
# first=1, middle=[2, 3, 4], last=5

# 交换变量（无需临时变量）
x, y = 10, 20
x, y = y, x
print(f"x={x}, y={y}")  # x=20, y=10

# 忽略不需要的值（用 _ 约定）
name, _, age = ("Alice", "secret", 30)
print(f"{name}, {age} 岁")

# 深层解包
person = ("Bob", (1990, 5, 15))
name, (year, month, day) = person
print(f"{name} 生于 {year}年{month}月{day}日")
```

**案例3：工业级 —— 函数返回多值（元组解包）**

```python
from typing import Tuple, Optional

class DivisionResult:
    """
    安全的除法操作。用多返回值模式替代异常抛出的做法（Go 风格）。
    在 Python 中常以元组形式返回 (success, result, error_message)。
    """

    @staticmethod
    def safe_divide(a: float, b: float) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        安全的除法。
        返回: (是否成功, 结果, 错误信息)
        """
        try:
            if b == 0:
                return False, None, "除数不能为零"
            return True, a / b, None
        except Exception as e:
            return False, None, str(e)


# 使用元组解包消费返回值
success, result, error = DivisionResult.safe_divide(10, 2)
if success:
    print(f"结果: {result}")      # 结果: 5.0
else:
    print(f"错误: {error}")

success, result, error = DivisionResult.safe_divide(10, 0)
if not success:
    print(f"错误: {error}")       # 错误: 除数不能为零


# 另一个工业级用法：namedtuple 让多返回值更语义化
from collections import namedtuple

CommandResult = namedtuple("CommandResult", ["success", "output", "error"])

def run_command(cmd: str) -> CommandResult:
    """执行命令，返回命名元组"""
    import subprocess
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return CommandResult(
            success=result.returncode == 0,
            output=result.stdout.strip(),
            error=result.stderr.strip() if result.returncode != 0 else None,
        )
    except Exception as e:
        return CommandResult(success=False, output=None, error=str(e))

# 使用
# r = run_command("ls -la")
# print(f"成功: {r.success}, 输出前100字符: {str(r.output)[:100]}")
```

---

## 4.3 字典 (dict) —— 最核心

### 知识点：字典的增删改查

**案例1：安全取值的方法对比**

```python
user = {"name": "Alice", "age": 30}

# 方式1：直接索引 —— 键不存在抛 KeyError
print(user["name"])       # Alice
# print(user["email"])    # KeyError!

# 方式2：get() —— 键不存在返回 None 或默认值（推荐）
print(user.get("email"))            # None
print(user.get("email", "N/A"))     # "N/A"

# 方式3：setdefault —— 键不存在时设置默认值并返回
# 常用于分组、计数场景
email = user.setdefault("email", "unknown@example.com")
print(user)  # {'name': 'Alice', 'age': 30, 'email': 'unknown@example.com'}

# 方式4：collections.defaultdict —— 自动创建默认值
from collections import defaultdict

# 按首字母分组
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
by_letter = defaultdict(list)   # 当键不存在时，自动调用 list() 创建空列表
for word in words:
    by_letter[word[0]].append(word)
print(dict(by_letter))
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

**案例2：字典的合并与更新**

```python
# update(): 就地合并
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
d1.update(d2)
print(d1)  # {'a': 1, 'b': 3, 'c': 4} — 同名的键被覆盖

# | 运算符（Python 3.9+）：返回新字典
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
merged = d1 | d2
print(merged)   # {'a': 1, 'b': 3, 'c': 4}
print(d1)       # {'a': 1, 'b': 2} — 原字典不变

# |= 运算符（Python 3.9+）：就地合并
d1 |= d2
print(d1)       # {'a': 1, 'b': 3, 'c': 4}

# ** 解包合并（兼容旧版本）
merged = {**d1, **d2}   # 后面的覆盖前面的同名键
print(merged)   # {'a': 1, 'b': 3, 'c': 4}
```

**案例3：工业级 —— LRU 缓存（最近最少使用淘汰）**

```python
from collections import OrderedDict
from typing import Optional, TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")

class LRUCache(Generic[K, V]):
    """
    基于 OrderedDict 的 LRU 缓存。
    当超过容量时，淘汰最久未使用的条目。
    所有操作时间复杂度 O(1)。

    使用场景: 本地缓存、会话管理、DNS 缓存等。
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("容量必须大于0")
        self.capacity = capacity
        self._cache: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> Optional[V]:
        """获取值，并将该项移到末尾（标记为最近使用）"""
        if key not in self._cache:
            return None
        # move_to_end: 移到末尾 = 最近使用
        self._cache.move_to_end(key)
        return self._cache[key]

    def put(self, key: K, value: V) -> None:
        """设置值。如果 key 存在则更新并移到末尾；如果超出容量则淘汰最旧的"""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            # popitem(last=False): 弹出第一个 = 最久未使用
            oldest_key, oldest_value = self._cache.popitem(last=False)
            print(f"淘汰: {oldest_key} -> {oldest_value}")

    def __repr__(self):
        return f"LRUCache({list(self._cache.items())})"


# 使用演示
cache = LRUCache[str, str](capacity=3)
cache.put("a", "数据A")
cache.put("b", "数据B")
cache.put("c", "数据C")
print(cache)  # [('a', '数据A'), ('b', '数据B'), ('c', '数据C')]

cache.get("a")          # 访问 a，移到末尾
cache.put("d", "数据D")  # 加入 d，淘汰最久未使用的 b
print(cache)  # [('c', '数据C'), ('a', '数据A'), ('d', '数据D')]
```

---

### 知识点：Counter 计数器

**案例1：Counter 基础用法**

```python
from collections import Counter

# 快速统计
text = "abracadabra"
counter = Counter(text)
print(counter)  # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})

# 从可迭代对象创建
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
word_count = Counter(words)
print(word_count)  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})

# 取最常见的 N 个
print(word_count.most_common(2))  # [('apple', 3), ('banana', 2)]

# Counter 之间的运算
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)   # Counter({'a': 4, 'b': 3})  — 相加
print(c1 - c2)   # Counter({'a': 2})           — 相减（结果只保留正数）
print(c1 & c2)   # Counter({'a': 1, 'b': 1})  — 取每个键的最小值
print(c1 | c2)   # Counter({'a': 3, 'b': 2})  — 取每个键的最大值
```

**案例2：Counter 的实际应用**

```python
from collections import Counter

# 分析两份日志的差异
yesterday = Counter(["error", "info", "error", "warn", "info"])
today     = Counter(["error", "info", "info", "info", "error", "debug"])

# 哪种日志增多了？
print("相比昨天增加:", today - yesterday)     # Counter({'info': 2, 'debug': 1})
# 哪种日志减少了？
print("相比昨天减少:", yesterday - today)     # Counter({'warn': 1})
```

**案例3：工业级 —— 访问频率限流器**

```python
import time
from collections import Counter, deque
from typing import Deque, Tuple

class RateLimiter:
    """
    基于滑动时间窗口的限流器。
    用 Counter + 时间戳队列实现，无需外部依赖。
    常用于 API 限流、登录频率限制等场景。
    """

    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: Deque[float] = deque()

    def is_allowed(self, client_id: str) -> bool:
        """检查请求是否被允许"""
        now = time.time()

        # 清除窗口外的旧请求
        cutoff = now - self.window
        while self._requests and self._requests[0] < cutoff:
            self._requests.popleft()

        # 检查是否超出限制
        if len(self._requests) >= self.max_requests:
            return False

        self._requests.append(now)
        return True


# 演示（快速连续请求）
limiter = RateLimiter(max_requests=3, window_seconds=1.0)
for i in range(5):
    allowed = limiter.is_allowed("user_1")
    print(f"请求 {i+1}: {'✅ 通过' if allowed else '❌ 限流'}")
# 请求 1: ✅ 通过
# 请求 2: ✅ 通过
# 请求 3: ✅ 通过
# 请求 4: ❌ 限流
# 请求 5: ❌ 限流
# 等1秒后再请求就会通过
```

---

## 4.4 集合 (set)

### 知识点：集合运算

**案例1：集合的基础操作**

```python
# 创建集合（注意空集合必须用 set()，因为 {} 是空字典）
s = {1, 2, 3, 3, 2, 1}   # 自动去重
print(s)                   # {1, 2, 3}

empty_set = set()          # 空集合
empty_dict = {}            # 空字典！

# 添加和删除
s.add(4)                   # 添加一个元素
s.update([5, 6, 7])        # 批量添加（同 extend）
s.discard(100)             # 删除元素（不存在也不报错）
s.remove(5)                # 删除元素（不存在抛 KeyError）
print(s)                   # {1, 2, 3, 4, 6, 7}

# 成员判断 O(1)
print(3 in s)              # True（比列表 O(n) 快得多！）
```

**案例2：集合运算的实战**

```python
# 两组用户
vip_users = {"Alice", "Bob", "Charlie", "David"}
active_users = {"Charlie", "David", "Eve", "Frank"}

# 交集 &：既是 VIP 又是活跃用户
print(vip_users & active_users)    # {'Charlie', 'David'}

# 并集 |：VIP 或活跃用户
print(vip_users | active_users)    # {'Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank'}

# 差集 -：是 VIP 但不活跃（流失风险！）
print(vip_users - active_users)    # {'Alice', 'Bob'}

# 对称差集 ^：只在其中一边的（VIP 或活跃，但不同时满足）
print(vip_users ^ active_users)    # {'Alice', 'Bob', 'Eve', 'Frank'}

# 子集和超集
a = {1, 2}
b = {1, 2, 3, 4}
print(a <= b)  # True — a 是 b 的子集
print(b >= a)  # True — b 是 a 的超集
print(a < b)   # True — a 是 b 的真子集（不等）
```

**案例3：工业级 —— 基于集合的推荐引擎（协同过滤简化版）**

```python
from typing import Dict, Set, List, Tuple

class SimpleRecommender:
    """
    基于 Jaccard 相似度的简化推荐引擎。
    根据用户的行为集合，找到最相似的用户，推荐他们喜欢但当前用户没接触过的物品。

    Jaccard 相似度 = |A ∩ B| / |A ∪ B|
    """

    def __init__(self):
        self._user_likes: Dict[str, Set[str]] = {}   # 用户 -> 喜欢的东西

    def add_likes(self, user: str, items: Set[str]):
        if user not in self._user_likes:
            self._user_likes[user] = set()
        self._user_likes[user].update(items)

    def jaccard_similarity(self, a: Set[str], b: Set[str]) -> float:
        """计算两个集合的 Jaccard 相似度"""
        if not a or not b:
            return 0.0
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union

    def recommend(self, user: str, top_n: int = 5) -> List[Tuple[str, float]]:
        """为指定用户推荐物品"""
        if user not in self._user_likes:
            return []

        user_items = self._user_likes[user]
        candidates: Dict[str, float] = {}  # 候选物品 -> 推荐分数

        for other, other_items in self._user_likes.items():
            if other == user:
                continue

            similarity = self.jaccard_similarity(user_items, other_items)
            if similarity == 0:
                continue

            # 找到对方喜欢但当前用户没接触过的物品
            new_items = other_items - user_items     # 差集
            for item in new_items:
                # 推荐分数 = 相似度累加（多个相似用户喜欢同一物品会加分）
                candidates[item] = candidates.get(item, 0) + similarity

        # 按推荐分数排序，返回 top N
        sorted_items = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_n]


# 使用演示
rec = SimpleRecommender()
rec.add_likes("Alice", {"Python", "Go", "Docker"})
rec.add_likes("Bob",   {"Python", "Go", "Kubernetes", "Terraform"})
rec.add_likes("Charlie", {"Java", "Docker", "Kubernetes"})

print("给 Alice 推荐:")
for item, score in rec.recommend("Alice", top_n=3):
    print(f"  {item}: 相似度得分 {score:.3f}")
# Kubernetes: ...（Bob 和 Charlie 都喜欢，但 Alice 还没接触）
# Terraform: ...（只有 Bob 喜欢）
# Java: ...（只有 Charlie 喜欢）
```

---

## 本章速查

| 操作 | list | tuple | dict | set |
|------|------|-------|------|-----|
| 创建 | `[1,2,3]` | `(1,2,3)` | `{"a":1}` | `{1,2,3}` |
| 空容器 | `[]` | `()` | `{}` | `set()` |
| 添加 | `append()` | ❌ 不可变 | `d[k]=v` | `add()` |
| 删除 | `pop()` `remove()` | ❌ | `pop()` `del` | `remove()` `discard()` |
| 成员判断 | `x in lst` O(n) | `x in tup` O(n) | `k in d` O(1) | `x in s` O(1) |
| 推导式 | `[x for ...]` | `tuple(x for ...)` | `{k:v for ...}` | `{x for ...}` |

| 何时用 | 场景 |
|--------|------|
| list | 有序、可修改、需要索引 |
| tuple | 不可变序列（常量、多返回值、字典键） |
| dict | 键值映射、查找、缓存、计数 |
| set | 去重、集合运算、成员判断（O(1)） |
