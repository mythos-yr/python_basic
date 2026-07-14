# 第四章：内置容器类型

> 这是 Python 中最核心的一章。list、tuple、dict、set 四种容器，覆盖日常开发 80% 的场景。

---

## 4.1 四种容器全景对比

### 理论：什么时候用哪个？

在写任何代码之前，先想清楚：你的数据是什么形态？

| 数据形态 | 用什么 | 为什么 |
|----------|--------|--------|
| 有序、会增减、需要索引 | **list** | 动态数组，支持下标访问和切片 |
| 不可变的有序数据（坐标、常量） | **tuple** | 轻量、可哈希（可做 dict 的键） |
| 键→值的映射（查找、缓存、计数） | **dict** | 哈希表，O(1) 查找速度 |
| 去重、集合运算（交集、差集） | **set** | 哈希表，O(1) 成员判断 |

```python
# 用一句话记住各自的特征：
list  = [1, 2, 3]     # 中括号，有序可变
tuple = (1, 2, 3)     # 小括号，有序不可变
dict  = {"a": 1}      # 花括号+冒号，键值对
set   = {1, 2, 3}     # 花括号无冒号，无序不重复（注意：{} 是空字典！）
```

**底层原理（通俗版）**：

- **list/tuple**：内存中连续排列，通过"第几个"（索引）快速访问。list 可变是因为内存分配了预留空间；tuple 不可变是刻意锁定了大小。
- **dict/set**：基于**哈希表**。想象一排邮箱，每个数据根据自身内容算出一个"邮箱号"，直接放进对应邮箱。查找时不需要挨个翻，直接算邮箱号去找——所以 O(1)。

**dict 的键为什么必须是不可变的？** 因为哈希值必须稳定。如果键变了，哈希值就变了，"邮箱号"不对了，就找不到了。

---

## 4.2 列表 (list)

### 理论：动态数组

list 是 Python 最常用的容器。底层是 C 语言数组，预分配了多余空间，所以 `append` 很快（大多数情况下 O(1)）。

---

### 关键字/方法速查

**增**：

| 方法 | 做什么 | 时间 |
|------|--------|------|
| `lst.append(x)` | 末尾加一个元素 | O(1) |
| `lst.insert(i, x)` | 在位置 i 插入（后面元素后移） | O(n) |
| `lst.extend(seq)` | 展开并逐个追加（= `+=`） | O(k) |

**删**：

| 方法 | 做什么 |
|------|--------|
| `lst.pop(i)` | 删除并返回索引 i 的元素（默认最后一个） |
| `lst.remove(x)` | 删除第一个值为 x 的元素 |
| `del lst[i]` | 按索引删除（可删切片） |
| `lst.clear()` | 清空 |

**查和排序**：

| 方法 | 做什么 |
|------|--------|
| `lst.index(x)` | 查找 x 第一次出现的位置 |
| `lst.count(x)` | 统计 x 出现次数 |
| `lst.sort(key=..., reverse=...)` | 原地排序 |
| `sorted(lst, key=...)` | 返回排序后的新列表（原列表不变） |

**`append` vs `extend` 的区别（面试高频）**：

```python
a = [1,2]; a.append([3,4])   # [1, 2, [3, 4]]  —— 整个列表当做一个元素
a = [1,2]; a.extend([3,4])   # [1, 2, 3, 4]    —— 展开追加
```

---

### 案例

**案例1：sort 的 key 参数——按任意规则排序**

```python
# 按字符串长度排序
words = ["python", "go", "rust", "c", "javascript"]
print(sorted(words, key=len))  # ['c', 'go', 'rust', 'python', 'javascript']

# 多级排序：先按年龄，再按名字
people = [("Alice", 25), ("Bob", 30), ("Charlie", 25)]
print(sorted(people, key=lambda p: (p[1], p[0])))
# [('Alice', 25), ('Charlie', 25), ('Bob', 30)]

# 反向排序（数字降序 + 字符串升序）
data = [("A", 10), ("B", 5), ("C", 10)]
print(sorted(data, key=lambda x: (-x[1], x[0])))
# [('A', 10), ('C', 10), ('B', 5)]
```

**案例2：列表去重并保持原始顺序**

```python
# 方式1：dict.fromkeys（Python 3.7+ dict 保持插入顺序）
items = [3, 1, 4, 1, 5, 9, 2, 6, 5]
unique = list(dict.fromkeys(items))
print(unique)  # [3, 1, 4, 5, 9, 2, 6]

# 方式2：手动去重（兼容旧版本）
seen = set()
unique = [x for x in items if not (x in seen or seen.add(x))]
```

**案例3：深浅拷贝——理解赋值 vs 复制**

```python
import copy

original = [1, 2, [10, 20]]

# 赋值：不是拷贝，是多一个引用
ref = original            # ref is original → True

# 浅拷贝：外层新列表，内层共享引用
shallow = copy.copy(original)
shallow[2].append(30)     # original[2] 也被影响！

# 深拷贝：递归复制，完全独立
deep = copy.deepcopy(original)
deep[2].append(40)        # original 不受影响
```

---

## 4.3 元组 (tuple)

### 理论：不可变的轻量列表

tuple 和 list 几乎一样，但**不可变**（创建后不能增删改）。这带来了两个优势：

1. **更安全**：不能意外修改，适合存储常量
2. **可哈希**：可以作为 dict 的键和 set 的元素

---

### 关键字/语法

```python
(1, 2, 3)     # 标准创建
1, 2, 3       # 括号可以省略（打包）
(1,)          # ⚠️ 单元素必须加逗号！(1) 只是整数 1
()            # 空元组
a, b = (1, 2) # 解包
a, *b = (1, 2, 3, 4)  # 星号解包：a=1, b=[2,3,4]
```

---

### 案例

**案例1：元组解包——交换变量、多返回值**

```python
# 交换变量（不需要临时变量）
a, b = 10, 20
a, b = b, a
print(a, b)  # 20, 10

# 函数返回多值（本质是返回元组）
def min_max(items):
    return min(items), max(items)

low, high = min_max([3, 1, 4, 1, 5])
print(low, high)  # 1, 5
```

**案例2：星号解包——收集剩余元素**

```python
first, *middle, last = (1, 2, 3, 4, 5)
print(first)    # 1
print(middle)   # [2, 3, 4]（注意：middle 是列表）
print(last)     # 5
```

**案例3：namedtuple——给元组字段命名**

```python
from collections import namedtuple

# 传统元组：通过索引访问，不直观
# point = (3, 4)
# print(point[0])  # 3 —— 什么意思？x 还是 y？

# namedtuple：字段有名字
Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x, p.y)  # 3, 4 —— 清晰！

# 工业用法：表示数据库查询结果
User = namedtuple("User", ["id", "name", "email"])
user = User(1, "Alice", "alice@example.com")
print(user.name)
```

---

## 4.4 字典 (dict) —— 最核心

### 理论：哈希表实现的高速键值存储

dict 内部是**哈希表**。取 `d[key]` 时，Python 计算 key 的哈希值，直接定位到存储位置——不需要遍历，所以 O(1)。

**类比**：dict 像现实中的字典。你要查"apple"这个词（键），不是从第一页开始翻，而是根据拼音索引直接翻到对应的页（哈希），找到释义（值）。

**键的可哈希要求**：list 不能做键（因为可变，哈希值会变），tuple 可以（不可变）。dict 和 set 也不能做键。

---

### 关键字/方法速查

**安全取值（四选一）**：

```python
d["key"]             # 直接取 —— 键不存在抛 KeyError
d.get("key")         # 安全取 —— 键不存在返 None
d.get("key", "默认") # 安全取 —— 键不存在返默认值
d.setdefault("key", "默认")  # 不存在就设置并返回默认值
```

**增删改**：

```python
d["key"] = value       # 设置/更新
d.update({k: v})       # 批量更新
d.pop("key")            # 删除并返回值
del d["key"]            # 删除
```

**遍历**：

```python
for key in d:               # 遍历键
for key in d.keys():        # 同上（显式）
for value in d.values():    # 遍历值
for key, value in d.items(): # 同时遍历键值（最常用）
```

**合并**：

```python
d1 | d2              # Python 3.9+，返回合并后的新字典
{**d1, **d2}         # 旧版兼容写法
```

---

### 案例

**案例1：Counter——统计频次**

```python
from collections import Counter

text = "abracadabra"
c = Counter(text)
print(c)                    # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(c.most_common(2))     # [('a', 5), ('b', 2)]

# Counter 之间可以做运算
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)  # Counter({'a': 4, 'b': 3})
```

**案例2：defaultdict——自动创建默认值**

```python
from collections import defaultdict

# ❌ 普通 dict：需要判断键是否存在
word_groups = {}
for word in ["apple", "banana", "avocado"]:
    first = word[0]
    if first not in word_groups:
        word_groups[first] = []
    word_groups[first].append(word)

# ✅ defaultdict：自动创建
word_groups = defaultdict(list)
for word in ["apple", "banana", "avocado"]:
    word_groups[word[0]].append(word)
# {'a': ['apple', 'avocado'], 'b': ['banana']}
```

**案例3：LRU 缓存——用 OrderedDict 实现淘汰策略**

```python
from collections import OrderedDict

class LRUCache:
    """最近最少使用缓存——超出容量时淘汰最旧的数据"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self._cache = OrderedDict()

    def get(self, key):
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)  # 标记为最近使用
        return self._cache[key]

    def put(self, key, value):
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)  # 弹出最旧的
```

---

## 4.5 集合 (set)

### 理论：没有重复元素的哈希表

set 可以理解为"只有键、没有值的 dict"。底层同样是哈希表，所以成员判断 O(1)。

**核心用途**：去重、成员判断、集合运算（交集、并集、差集）。

**注意**：`{}` 是空字典，空集合必须用 `set()`。

---

### 关键字/语法

| 运算 | 符号 | 方法 | 含义 |
|------|------|------|------|
| 并集 | `A \| B` | `A.union(B)` | 在 A 或 B 中 |
| 交集 | `A & B` | `A.intersection(B)` | 同时在 A 和 B 中 |
| 差集 | `A - B` | `A.difference(B)` | 在 A 但不在 B 中 |
| 对称差 | `A ^ B` | `A.symmetric_difference(B)` | 只在其中一边 |

---

### 案例

**案例1：用 set 去重和成员判断**

```python
# 去重
nums = [1, 2, 2, 3, 3, 3]
unique = list(set(nums))    # 注意：set 不保持顺序
print(unique)               # [1, 2, 3]

# 成员判断 O(1)——比 list 快得多
data = {1, 2, 3, 4, 5}
print(3 in data)   # True（O(1)）
```

**案例2：集合运算——找到两种用户的交集**

```python
vip_users = {"Alice", "Bob", "Charlie"}
active_users = {"Charlie", "David", "Eve"}

print(vip_users & active_users)   # {'Charlie'}     —— VIP且活跃
print(vip_users - active_users)   # {'Alice', 'Bob'} —— VIP但不活跃（流失风险！）
print(vip_users ^ active_users)   # 只在一边的用户
```

**案例3：用 set 快速做数据差异比较（工业场景）**

```python
# 比较两个文件中的 ID 列表，找出新增和删除的
yesterday_ids = {101, 102, 103, 104, 105}
today_ids = {103, 104, 105, 106, 107}

new_ids = today_ids - yesterday_ids     # {106, 107} —— 新增
deleted_ids = yesterday_ids - today_ids # {101, 102} —— 删除
unchanged = yesterday_ids & today_ids   # {103, 104, 105} —— 不变

print(f"新增: {new_ids}, 删除: {deleted_ids}")
```

---

## 本章速查

| 操作 | list | tuple | dict | set |
|------|------|-------|------|-----|
| 创建 | `[1,2]` | `(1,2)` | `{"k":"v"}` | `{1,2}` |
| 空容器 | `[]` | `()` | `{}` | `set()` |
| 加元素 | `append(x)` | 不可变 | `d[k]=v` | `add(x)` |
| 删元素 | `pop()`/`remove(x)` | 不可变 | `pop(k)`/`del d[k]` | `discard(x)` |
| 成员判断 | `x in lst` O(n) | O(n) | `k in d` O(1) | `x in s` O(1) |
| 遍历 | `for x in lst` | 同左 | `for k,v in d.items()` | `for x in s` |
