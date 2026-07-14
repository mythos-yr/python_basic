# 第四章：内置容器类型

> Python 中最核心的一章。list、tuple、dict、set 四种容器，覆盖日常开发 80% 的场景。

---

## 4.1 四种容器全景对比

### 理论：什么时候用哪个？

在写任何代码之前，先想清楚：你的数据是什么**形态**？

| 数据形态 | 用什么 | 为什么 |
|----------|--------|--------|
| 有序、会增减、需要索引 | **list** | 动态数组，支持下标访问和切片 |
| 不可变的有序数据 | **tuple** | 轻量、可哈希（可做 dict 的键） |
| 键→值的映射（查找、计数） | **dict** | 哈希表，O(1) 查找 |
| 去重、集合运算（交/并/差） | **set** | 哈希表，O(1) 成员判断 |

```python
list  = [1, 2, 3]      # 中括号，有序可变
tuple = (1, 2, 3)      # 小括号，有序不可变
dict  = {"a": 1}       # 花括号+冒号，键值对
set   = {1, 2, 3}      # 花括号无冒号（注意：{} 是空字典！）
```

**底层原理（通俗版）**：

- **list/tuple**：内存中连续排列，通过索引 O(1) 访问。list 预分配多余空间，append 很快；tuple 锁定大小不可变。
- **dict/set**：**哈希表**。类比一排邮箱，每个数据根据自身内容算一个"邮箱号"，直接放进对应邮箱。查找不需要挨个翻，直接算邮箱号找到——所以 O(1)。
- **dict 的键为什么必须是不可变的？** 哈希值必须稳定。键变了 → 哈希值变了 → "邮箱号"不对了 → 找不到了。

---

## 4.2 列表 (list)

### 理论：动态数组

list 底层是 C 语言数组，预分配额外空间，所以 `append` 大多数情况是 O(1)。在中间插入或删除元素时需要移动后续元素，是 O(n)。

---

### 知识点：列表的增删改查——逐个详解

**增——四种方式，行为各不相同**：

| 方法 | 做什么 | 时间复杂度 | 返回值 |
|------|--------|-----------|--------|
| `lst.append(x)` | 在末尾加**一个**元素 | O(1) | None |
| `lst.insert(i, x)` | 在位置 i 插入，后面元素整体后移 | O(n) | None |
| `lst.extend(seq)` | 展开可迭代对象，**逐个**追加到末尾 | O(k) | None |
| `+` / `+=` | `+` 返回新列表；`+=` 等价 extend | O(n+k) | 新列表/None |

**删——五种方式，行为各不相同**：

| 方法 | 做什么 | 返回值 | 不存在的处理 |
|------|--------|--------|-------------|
| `lst.pop(i)` | 删除并返回索引 i 的元素（默认最后一个） | 被删元素 | 抛 IndexError |
| `lst.remove(x)` | 删除**第一个**值为 x 的元素 | None | 抛 ValueError |
| `del lst[i]` | 按索引删除，可删切片 `del lst[1:3]` | 无 | 抛 IndexError |
| `lst.clear()` | 清空所有元素 | None | 安全 |
| `lst.pop(0)` | 删除第一个元素（O(n)，所有元素前移） | 被删元素 | 抛 IndexError |

**排序——sort() vs sorted()**：

| 方法 | 原地修改？ | 返回值 | 适用范围 |
|------|-----------|--------|---------|
| `lst.sort(key=..., reverse=...)` | ✅ 修改原列表 | None | 仅 list |
| `sorted(it, key=..., reverse=...)` | ❌ 返回新列表 | 新列表 | 任何可迭代对象 |

**key 参数是理解排序的关键**：排序前，每个元素先经过 key 函数转换，用转换后的值来比较。比如 `sorted(words, key=len)` 意思是"用每个单词的长度来做比较"。

**拷贝**：

| 方式 | 深度 | 内层对象 |
|------|------|---------|
| `b = a` | 不拷贝（多贴标签） | 就是同一个对象 |
| `b = a.copy()` / `a[:]` / `list(a)` | **浅拷贝**：外层新列表 | 内层元素共享引用 |
| `b = copy.deepcopy(a)` | **深拷贝**：递归复制 | 内层也完全独立 |

---

### 案例

**案例1：append vs extend vs insert 的区别（面试必考）**

```python
# append: 把参数当成一个整体，加在末尾
nums = [1, 2, 3]
nums.append([4, 5])
print(nums)   # [1, 2, 3, [4, 5]]  ← [4,5] 作为单个元素

# extend: 展开参数，把里面的元素逐个加进去
nums = [1, 2, 3]
nums.extend([4, 5])
print(nums)   # [1, 2, 3, 4, 5]    ← 展开追加

# insert: 在指定位置插入
nums = [1, 2, 3]
nums.insert(1, "X")     # 在索引1处插入
print(nums)   # [1, 'X', 2, 3]     ← 后面元素全部后移

# + 运算符：返回新列表，原列表不变
a = [1, 2]; b = [3, 4]
c = a + b
print(a)     # [1, 2]   ← 没变
print(c)     # [1, 2, 3, 4]
```

**案例2：五种删除方式的对比**

```python
nums = [10, 20, 30, 40, 50, 20]

# pop(): 删除并返回（有返回值，"弹出来"）
last = nums.pop()        # 默认删最后一个
print(f"pop(): {nums}, 返回值: {last}")   # [10,20,30,40,50], 20

second = nums.pop(1)     # 删索引1的元素
print(f"pop(1): {nums}, 返回值: {second}") # [10,30,40,50], 20

# remove(): 按值删除（删第一个匹配的，无返回值）
nums = [1, 2, 3, 2, 4]
nums.remove(2)           # 删除第一个2
print(f"remove(2): {nums}")   # [1, 3, 2, 4]

# del: 按索引删（可删切片）
nums = [1, 2, 3, 4, 5]
del nums[1]              # 删索引1
print(f"del[1]: {nums}")       # [1, 3, 4, 5]
del nums[1:3]            # 删切片 1:3（删两个）
print(f"del[1:3]: {nums}")     # [1, 5]

# clear(): 清空
nums.clear()
print(f"clear(): {nums}")      # []
```

**案例3：sort 的 key 参数——多级排序和自定义排序**

```python
# 按字符串长度排序
words = ["python", "go", "rust", "c", "javascript"]
print(sorted(words, key=len))  # ['c', 'go', 'rust', 'python', 'javascript']

# 多级排序：先按年龄升序，同龄再按姓名字母序
people = [("Alice", 25), ("Bob", 30), ("Charlie", 25)]
print(sorted(people, key=lambda p: (p[1], p[0])))
# [('Alice', 25), ('Charlie', 25), ('Bob', 30)]

# 降序技巧：用负号（只对数字有效）
data = [("A", 10), ("B", 5), ("C", 10)]
print(sorted(data, key=lambda x: (-x[1], x[0])))
# [('A', 10), ('C', 10), ('B', 5)]  ← 数字降序，字母升序

# 自然排序（人读排序）：file2 排在 file10 前面
import re
def natural_key(s):
    """把字符串中的数字段转为整数比较"""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", s)]

files = ["file10.txt", "file2.txt", "file1.txt"]
print(sorted(files, key=natural_key))
# ['file1.txt', 'file2.txt', 'file10.txt']  而非 ['file1.txt', 'file10.txt', 'file2.txt']
```

**案例4：深浅拷贝——赋值 vs 浅拷贝 vs 深拷贝的区别**

```python
import copy

original = [1, 2, [10, 20]]

# 1. 赋值（=）：多贴一个标签，同一个对象
ref = original
print(f"ref is original: {ref is original}")    # True

# 2. 浅拷贝：外层新列表，内层共享引用
shallow = copy.copy(original)   # 或 original.copy(), original[:]
print(f"shallow is original: {shallow is original}")        # False
print(f"shallow[2] is original[2]: {shallow[2] is original[2]}")  # True！内层共享

original[2].append(30)
print(f"浅拷贝受影响: shallow[2] = {shallow[2]}")   # [10, 20, 30]

# 3. 深拷贝：递归复制所有层级，完全独立
deep = copy.deepcopy(original)
original[2].append(40)
print(f"深拷贝不受影响: deep[2] = {deep[2]}")       # [10, 20, 30]
```

**案例5（工业级）：列表去重并保持原始顺序**

```python
# 方法1：dict.fromkeys（Python 3.7+ 推荐，dict 保持插入顺序）
items = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
unique = list(dict.fromkeys(items))
print(unique)  # [3, 1, 4, 5, 9, 2, 6]

# 方法2：手动用 set + 列表推导式
seen = set()
unique = [x for x in items if not (x in seen or seen.add(x))]
print(unique)  # [3, 1, 4, 5, 9, 2, 6]

# 按某个字段去重（保留第一次出现的记录）
records = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice_Dup"},   # 重复 id
]
seen_ids = set()
unique_records = [r for r in records if not (r["id"] in seen_ids or seen_ids.add(r["id"]))]
print(unique_records)  # 保留前两条，丢弃第三条
```

---

## 4.3 元组 (tuple)

### 理论：不可变的轻量列表

tuple 和 list 几乎一样，但**不可变**——创建后不能增删改。好处：

1. **更安全**：不能意外修改，适合存常量
2. **可哈希**：可以做 dict 的键和 set 的元素
3. **更快**：解释器知道它不会变，可以做优化

**注意**："不可变"指引用不可变。如果 tuple 里包含 list，list 里的内容仍然可以改。

---

### 知识点：创建、解包、namedtuple

**创建**：

```python
(1, 2, 3)     # 标准方式
1, 2, 3       # 括号可以省略（打包）
(1,)          # ⚠️ 单元素元组必须加逗号！(1) 就是整数 1
()            # 空元组
tuple([1,2])  # 从其他可迭代对象转换
```

**解包（unpacking）**：

```python
a, b = (1, 2)              # 基础解包
a, *b = (1, 2, 3, 4)       # 星号吞掉剩余元素，b 是列表
a, *_, b = (1, 2, 3, 4)    # _ 表示"我不关心这个值"
```

**namedtuple**：让元组的每个位置有语义化的名字，代码更可读。

---

### 案例

**案例1：元组不可变性的深入理解**

```python
# 不可变意味着不能增删改
t = (1, 2, 3)
# t[0] = 10     # TypeError!
# t.append(4)   # AttributeError!

# 但"不可变"只针对元组本身的引用——如果元组包含可变对象...
t = (1, [2, 3], 4)
t[1].append(5)           # ✅ 可以！修改的是列表的内容，不是元组的引用
print(t)                  # (1, [2, 3, 5], 4)

# 元组的 id 没变，变的只是它引用的列表的内容
```

**案例2：解包的各种姿势**

```python
# 交换变量（Python 独有，无需临时变量）
a, b = 10, 20
a, b = b, a
print(a, b)  # 20, 10

# 函数多返回值（本质是返回元组）
def get_min_max_avg(numbers):
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

low, high, avg = get_min_max_avg([3, 1, 4, 1, 5])
print(f"最小:{low}, 最大:{high}, 平均:{avg:.2f}")

# 星号解包——收集多余元素
first, *middle, last = (1, 2, 3, 4, 5)
print(f"first={first}, middle={middle}, last={last}")
# first=1, middle=[2,3,4], last=5

# 深层解包
person = ("Bob", (1990, 5, 15))
name, (year, month, day) = person
print(f"{name}生于{year}年{month}月{day}日")
```

**案例3：namedtuple——给元组每个位置取名**

```python
from collections import namedtuple

# 传统元组：只能靠索引访问 → 不直观
# record = ("Alice", 30, "Beijing")
# print(record[2])  # Beijing —— 读者不知道[2]是什么

# namedtuple：每个字段都有名字
Person = namedtuple("Person", ["name", "age", "city"])
p = Person("Alice", 30, "Beijing")
print(p.name, p.age, p.city)   # 清晰！

# 工业用法：表示数据库查询结果、API 返回值、CSV 行
Order = namedtuple("Order", ["id", "amount", "status"])
orders = [Order(1, 99.9, "paid"), Order(2, 199.9, "shipped")]
for o in orders:
    print(f"订单{o.id}: ¥{o.amount} [{o.status}]")
```

---

## 4.4 字典 (dict)

### 理论：哈希表实现的高速键值存储

dict 内部是**哈希表**。`d[key]` 时，Python 计算 key 的哈希值，直接定位存储位置——不需要遍历，O(1)。

**类比**：dict 像英汉字典。查 "apple" 不是从第一页开始翻，而是根据拼音索引直接翻到对应页。

**键的要求**：必须是**可哈希的**（不可变类型）。list、dict、set 不能做键；int、str、tuple、frozenset 可以。

---

### 知识点：安全取值的四种方式

```python
d = {"name": "Alice"}

d["name"]                    # 直接取 —— 键不存在抛 KeyError
d.get("name")                # 安全取 —— 不存在返 None，不抛异常
d.get("name", "默认值")       # 安全取 + 默认值
d.setdefault("name", "默认")  # 不存在就设置进去，然后返回（无论原来有没有）
```

**`get` vs `setdefault` 的区别**：

- `get` 是**纯查询**，不会修改 dict
- `setdefault` 是**"确保存在"**——如果键不存在，就把它设成默认值，然后返回

---

### 知识点：字典遍历、合并、删除

**遍历的四种方式**：

```python
for key in d:                  # 遍历键（默认）
for key in d.keys():           # 同上（显式）
for value in d.values():       # 只遍历值
for key, value in d.items():   # 同时遍历键和值（最常用）
```

**合并的三种方式**：

```python
d1 | d2          # Python 3.9+，返回新字典
d1 |= d2         # Python 3.9+，就地合并
{**d1, **d2}     # 解包合并（旧版兼容），后面覆盖前面的同名键
d1.update(d2)    # 就地合并（修改 d1），返回 None
```

**删除**：

```python
d.pop("key")          # 删除并返回值；键不存在抛 KeyError
d.pop("key", default) # 删除并返回值；不存在返默认值
d.popitem()           # 删除并返回 (key, value)；Python 3.7+ 按 LIFO（最后插入的先弹出）
del d["key"]          # 删除；不存在抛 KeyError
d.clear()             # 清空
```

---

### 案例

**案例1：setdefault——分组和计数的利器**

```python
# 按首字母给单词分组
words = ["apple", "banana", "avocado", "blueberry", "cherry"]
groups = {}
for word in words:
    first = word[0]
    # setdefault: 如果 first 这个键不存在，就创建空列表
    groups.setdefault(first, []).append(word)

print(groups)
# {'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}

# 统计词频（和 Counter 做同样的事）
text = "abracadabra"
freq = {}
for char in text:
    freq[char] = freq.setdefault(char, 0) + 1
print(freq)  # {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
```

**案例2：Counter——一行代码完成频次统计**

```python
from collections import Counter

text = "abracadabra"
c = Counter(text)
print(c)                     # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(c.most_common(2))      # [('a', 5), ('b', 2)]   取 Top N

# Counter 之间可以相加、相减
yesterday = Counter(["error", "info", "error", "warn"])
today = Counter(["info", "info", "error", "debug"])
print(today - yesterday)    # Counter({'info': 1, 'debug': 1})  —— 哪些增多了？
print(yesterday - today)    # Counter({'warn': 1})              —— 哪些减少了？
```

**案例3：defaultdict——告别 "if key not in dict"**

```python
from collections import defaultdict

# ❌ 普通 dict：每次都要判断键是否存在
normal = {}
for word in ["apple", "banana", "avocado"]:
    first = word[0]
    if first not in normal:
        normal[first] = []
    normal[first].append(word)

# ✅ defaultdict：不存在的键自动调用 list() 创建空列表
dd = defaultdict(list)
for word in ["apple", "banana", "avocado"]:
    dd[word[0]].append(word)

print(dict(dd))  # {'a': ['apple', 'avocado'], 'b': ['banana']}

# defaultdict 的其他常见用法
dd_int = defaultdict(int)       # 不存在的键返回 0（计数器）
dd_set = defaultdict(set)       # 不存在的键返回空 set（去重分组）
dd_lambda = defaultdict(lambda: "默认值")   # 自定义默认值
```

**案例4（工业级）：LRU 缓存——用 OrderedDict 实现淘汰策略**

```python
from collections import OrderedDict

class LRUCache:
    """
    最近最少使用缓存。超出容量时，淘汰最久未访问的数据。
    所有操作 O(1)。
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache = OrderedDict()

    def get(self, key):
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)   # 这个 key 是"最近使用"的，移到末尾
        return self._cache[key]

    def put(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self.capacity:
            oldest = self._cache.popitem(last=False)  # 弹出最旧的（在开头）
            print(f"淘汰: {oldest[0]}")

# 容量为3的缓存
cache = LRUCache(3)
cache.put("a", 1); cache.put("b", 2); cache.put("c", 3)
print(list(cache._cache))     # ['a', 'b', 'c']
cache.get("a")                # 访问 a → a 变为最近使用
cache.put("d", 4)             # 加入 d，淘汰最旧的 b
print(list(cache._cache))     # ['c', 'a', 'd']
```

---

## 4.5 集合 (set)

### 理论：没有重复元素的哈希表

set 可以理解为"只有键、没有值的 dict"。底层同样是哈希表，O(1) 成员判断。

**核心用途**：去重、成员判断、集合运算。

**两个变体**：
- `set()`：可变集合，可以增删
- `frozenset()`：不可变集合，可哈希，能做 dict 键和 set 元素

---

### 知识点：集合的增删和运算

**增删**：

| 方法 | 做什么 | 不存在时 |
|------|--------|---------|
| `s.add(x)` | 添加一个元素 | — |
| `s.update(it)` | 批量添加（类似 extend） | — |
| `s.remove(x)` | 删除元素 | 抛 KeyError |
| `s.discard(x)` | 安全删除 | 什么都不做 |
| `s.pop()` | 随机弹出一个 | 抛 KeyError |

**集合运算**：

| 运算 | 符号 | 方法 | 含义 |
|------|------|------|------|
| 并集 | `A \| B` | `A.union(B)` | 在 A 或 B 中 |
| 交集 | `A & B` | `A.intersection(B)` | 同时在 A 和 B 中 |
| 差集 | `A - B` | `A.difference(B)` | 在 A 不在 B 中 |
| 对称差 | `A ^ B` | `A.symmetric_difference(B)` | 只在其中一边 |

**子集超集判断**：

```python
a <= b   # a 是 b 的子集？
a < b    # a 是 b 的真子集？
a >= b   # a 是 b 的超集？
```

---

### 案例

**案例1：remove vs discard vs pop 的区别**

```python
s = {1, 2, 3}

# remove: 元素不存在会报错
s.remove(2)
# s.remove(99)     # KeyError!

# discard: 元素不存在也不报错（安全删除）
s.discard(99)       # 什么都不发生

# pop: 随机弹出（因为 set 无序）
s = {1, 2, 3}
popped = s.pop()
print(f"弹出了: {popped}, 剩余: {s}")
```

**案例2：集合运算实战——用户行为分析**

```python
vip_users = {"Alice", "Bob", "Charlie", "David"}
active_users = {"Charlie", "David", "Eve", "Frank"}

print("VIP且活跃:", vip_users & active_users)        # {'Charlie', 'David'}
print("VIP但不活跃(流失风险):", vip_users - active_users)  # {'Alice', 'Bob'}
print("活跃非VIP(潜在客户):", active_users - vip_users)    # {'Eve', 'Frank'}
print("只在一边的:", vip_users ^ active_users)
print("全部用户:", vip_users | active_users)
```

**案例3（工业级）：快速比较两个数据集的新增和删除**

```python
yesterday = {101, 102, 103, 104, 105}
today     = {103, 104, 105, 106, 107}

added = today - yesterday        # {106, 107}
deleted = yesterday - today      # {101, 102}
unchanged = yesterday & today    # {103, 104, 105}

print(f"新增 {len(added)} 个, 删除 {len(deleted)} 个, 不变 {len(unchanged)} 个")
# 用于：数据库数据同步、文件差异对比、日志增量分析
```

**案例4：frozenset——不可变集合**

```python
# frozenset 是可哈希的，可以做 dict 的键
fs = frozenset([1, 2, 3])
# fs.add(4)         # AttributeError! 不可变

# 实际应用：用 frozenset 做键来记录"组合"信息
order_items = {
    frozenset(["apple", "banana"]): 25.0,
    frozenset(["apple", "orange"]): 30.0,
}
print(order_items[frozenset(["banana", "apple"])])  # 25.0（顺序不影响）
```

---

## 本章速查

| 操作 | list | tuple | dict | set |
|------|------|-------|------|-----|
| 创建 | `[1,2]` | `(1,2)` | `{"k":"v"}` | `{1,2}` |
| 空容器 | `[]` | `()` | `{}` | `set()` |
| 加元素 | `append(x)` | ❌ 不可变 | `d[k]=v` | `add(x)` |
| 删元素 | `pop()`/`remove()` | ❌ | `pop(k)`/`del d[k]` | `discard(x)` |
| 成员判断 | `x in lst` O(n) | O(n) | `k in d` O(1) | `x in s` O(1) |
| 遍历 | `for x in lst` | 同左 | `for k,v in d.items()` | `for x in s` |
| 特殊 | 切片、sort | 不可变、可哈希 | default, Counter | 交/并/差, frozenset |
