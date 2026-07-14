# 第七章：推导式

---

## 理论：推导式就是把 for 循环浓缩成一行

推导式（Comprehension）是 Python 从数学集合论借来的语法。数学中写：

> { x² | x ∈ {1,2,3,4,5}, x 是偶数 }

Python 中写：

```python
{x**2 for x in [1,2,3,4,5] if x % 2 == 0}
```

**Python 有四种推导式**，分别生成四种容器：

| 类型 | 语法 | 生成 | 求值时机 |
|------|------|------|---------|
| 列表推导式 | `[x for x in it]` | list | 立即（全在内存） |
| 字典推导式 | `{k:v for k,v in it}` | dict | 立即 |
| 集合推导式 | `{x for x in it}` | set | 立即 |
| 生成器表达式 | `(x for x in it)` | generator | **惰性**（用时才计算） |

**推导式的通用结构**：

```python
[表达式 for 变量 in 数据源 if 条件]
  ↑              ↑              ↑
  对每个元素      从哪拿          筛掉哪些
  做什么
```

**if 的位置决定含义（核心规则）**：

| 写法 | 含义 | 结果 |
|------|------|------|
| `[x for x in data if cond]` | **过滤**（for 后） | 元素数量可能变少 |
| `[A if cond else B for x in data]` | **变换**（for 前） | 元素数量不变 |

**铁律**：for 后的 if 是过滤器（筛掉不想要的），for 前的 if 是变换器（每个元素必须有个结果，所以需要 else）。

---

## 7.1 列表推导式

### 知识点详解

列表推导式是最常用的推导式，用方括号 `[...]` 包裹，**立即**在内存中生成完整列表。

**基本语法**：

```python
[表达式 for 变量 in 可迭代对象]
[表达式 for 变量 in 可迭代对象 if 条件]           # 带过滤
[表达式A if 条件 else 表达式B for 变量 in 可迭代对象]  # 带变换
[表达式 for 变量1 in 可迭代对象1 for 变量2 in 可迭代对象2]  # 嵌套
```

**性能**：列表推导式比等价的 for 循环快 30%-50%，因为 `append` 的属性查找在 C 层完成。

**注意事项**：
- 不要超过 2 层嵌套——超过就拆成 for 循环，否则可读性太差
- 不要为了省行数在推导式里写有副作用的操作（如 `print`、写文件）
- 大数据量时考虑用生成器表达式替代，避免内存问题

---

### 案例

**案例1：基础——从 for 循环到推导式的演变**

```python
# ❌ for 循环 4 行
squares = []
for i in range(10):
    if i % 2 == 0:
        squares.append(i ** 2)

# ✅ 推导式 1 行
squares = [i ** 2 for i in range(10) if i % 2 == 0]
print(squares)  # [0, 4, 16, 36, 64]
```

**案例2：if 在 for 后（过滤）vs if-else 在 for 前（变换）**

```python
nums = [1, 2, 3, 4, 5, 6]

# for 后的 if：过滤——不满足的丢弃，元素数量变少
evens = [x for x in nums if x % 2 == 0]
print(evens)  # [2, 4, 6]  ← 只剩 3 个

# for 前的 if-else：变换——所有元素保留，但值可能变
labels = ["偶" if x % 2 == 0 else "奇" for x in nums]
print(labels)  # ['奇', '偶', '奇', '偶', '奇', '偶']  ← 还是 6 个
```

**案例3：嵌套推导式——多层 for 的顺序和等价写法**

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# 展平：for 从左到右 = 从外到内
flat = [x for row in matrix for x in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 等价于：
flat = []
for row in matrix:      # ← 第一个 for = 最外层
    for x in row:        # ← 第二个 for = 内层
        flat.append(x)

# 嵌套 + 过滤：只取偶数
flat_evens = [x for row in matrix for x in row if x % 2 == 0]
print(flat_evens)  # [2, 4, 6, 8]
```

**案例4：列表推导式的常见误用**

```python
# ❌ 推导式做有副作用的事——创建了无用列表
[print(x) for x in range(5)]     # 用 for 循环即可
# for x in range(5): print(x)     # ✅

# ❌ 超过两层嵌套——拆成 for 循环更可读
result = [x for a in A for b in B for c in C if a+b>c]  # 读着费劲

# ❌ 重复计算——把复杂表达式提取出来或拆成 for 循环
# result = [expensive_func(x) for x in data if expensive_func(x) > 0]
# ✅ 用海象运算符（Python 3.8+）：
# result = [v for x in data if (v := expensive_func(x)) > 0]
```

**案例5（工业级）：数据清洗管道——推导式串联**

```python
import re

# 清洗手机号列表——每个推导式做一步
raw = ["138-1234-5678", "  ", "abc", "15912345678", "18800001111"]

# 步骤1: 去除非数字字符
step1 = [re.sub(r"\D", "", p) for p in raw]
# 步骤2: 过滤空值和格式不对的
step2 = [p for p in step1 if p and len(p) == 11 and p.startswith("1")]
# 步骤3: 格式化输出
result = [f"{p[:3]}-{p[3:7]}-{p[7:]}" for p in step2]

print(result)  # ['138-1234-5678', '159-1234-5678', '188-0000-1111']
```

---

## 7.2 字典推导式

### 知识点详解

字典推导式用 `{key: value for ...}` 语法，**立即**生成一个字典。

**基本语法**：

```python
{键表达式: 值表达式 for 变量 in 可迭代对象}
{键表达式: 值表达式 for 变量 in 可迭代对象 if 条件}
```

**核心用途**：
- 从两个列表构建字典（配合 zip）
- 键值互换
- 过滤并转换字典
- 对已有的字典做 transform

---

### 案例

**案例1：从列表构建字典（配合 zip）**

```python
# 两个列表 → 字典
keys = ["name", "age", "city"]
values = ["Alice", 30, "Beijing"]
d = {k: v for k, v in zip(keys, values)}
print(d)  # {'name': 'Alice', 'age': 30, 'city': 'Beijing'}

# 带索引的字典
words = ["apple", "banana", "cherry"]
indexed = {i: w for i, w in enumerate(words)}
print(indexed)  # {0: 'apple', 1: 'banana', 2: 'cherry'}
```

**案例2：键值互换**

```python
original = {"a": 1, "b": 2, "c": 3}

# 键值互换（注意：值必须是可哈希的）
swapped = {v: k for k, v in original.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}
```

**案例3：过滤并变换字典**

```python
scores = {"Alice": 85, "Bob": 92, "Charlie": 78, "David": 60}

# 只保留及格者，并将分数转为等级
grades = {
    name: "A" if score >= 90 else "B" if score >= 80 else "C"
    for name, score in scores.items()
    if score >= 60
}
print(grades)  # {'Alice': 'B', 'Bob': 'A', 'Charlie': 'C', 'David': 'C'}
```

**案例4（工业级）：配置键名转换——驼峰转蛇形**

```python
# 从 Java 风格配置转为 Python 风格
java_config = {"dbHost": "localhost", "dbPort": 5432, "maxPoolSize": 50}

def camel_to_snake(s):
    """dbHost → db_host"""
    return "".join(
        "_" + c.lower() if c.isupper() else c for c in s
    ).lstrip("_")

python_config = {camel_to_snake(k): v for k, v in java_config.items()}
print(python_config)  # {'db_host': 'localhost', 'db_port': 5432, 'max_pool_size': 50}
```

---

## 7.3 集合推导式

### 知识点详解

集合推导式用 `{x for ...}` 语法（注意和字典的区别：没有冒号），**立即**生成一个集合。

**基本语法**：

```python
{表达式 for 变量 in 可迭代对象}
{表达式 for 变量 in 可迭代对象 if 条件}
```

**核心用途**：
- **去重**——最常用的场景
- 提取字段做集合运算
- 过滤后转集合

**⚠️ 注意**：`{}` 是空字典！空集合必须用 `set()`。集合推导式至少要在花括号里有 `for`。

---

### 案例

**案例1：去重——集合推导式的基本用法**

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

# 去重（注意：不保持原始顺序）
unique = {x for x in nums}
print(unique)  # {1, 2, 3, 4, 5, 6, 9}

# 带过滤的去重：只保留大于 3 的元素
unique_big = {x for x in nums if x > 3}
print(unique_big)  # {4, 5, 6, 9}
```

**案例2：提取字段去重——分析不重复的值**

```python
records = [
    {"role": "admin", "dept": "IT"},
    {"role": "user", "dept": "HR"},
    {"role": "admin", "dept": "IT"},
    {"role": "manager", "dept": "Finance"},
]

# 有哪些不同的角色？
roles = {r["role"] for r in records}
print(roles)  # {'admin', 'manager', 'user'}

# 有哪些不同的部门？
depts = {r["dept"] for r in records}
print(depts)  # {'Finance', 'HR', 'IT'}
```

**案例3（工业级）：文本分析——提取两个文本中的共同词**

```python
text1 = "Python is great for data science and machine learning"
text2 = "Machine learning and deep learning need Python"

# 提取不重复的单词（转小写以不区分大小写）
words1 = {w.lower() for w in text1.split()}
words2 = {w.lower() for w in text2.split()}

print(f"文本1独有: {words1 - words2}")   # {'data', 'great', 'is', 'science', 'for'}
print(f"文本2独有: {words2 - words1}")   # {'deep', 'need'}
print(f"共同出现: {words1 & words2}")    # {'python', 'machine', 'and', 'learning'}
```

---

## 7.4 生成器表达式

### 知识点详解

生成器表达式用**圆括号** `(...)` 包裹，是**惰性求值**的——表达式本身不执行任何计算，只在迭代时才逐个产生值。

**基本语法**：

```python
(表达式 for 变量 in 可迭代对象)
(表达式 for 变量 in 可迭代对象 if 条件)
```

**和列表推导式的关键区别**：

| 特性 | 列表推导式 `[...]` | 生成器表达式 `(...)` |
|------|-------------------|---------------------|
| 返回类型 | list | generator |
| 求值时机 | 立即，全在内存 | 惰性，用时才算 |
| 内存占用 | 和元素数量成正比 | 恒定（几十字节） |
| 可否多次遍历 | ✅ 可以 | ❌ 只能一次 |
| 可否索引/切片 | ✅ `lst[0]` | ❌ 不行 |

**省略括号的规则**：当生成器表达式是**函数的唯一参数**时，可以省略外层括号：

```python
sum((x for x in data))   # 完整写法
sum(x for x in data)     # 省略括号 ✓
```

---

### 案例

**案例1：内存占用的天壤之别**

```python
import sys

# 列表推导式：10万个结果全部在内存中
lst = [x ** 2 for x in range(100_000)]
print(f"列表: {sys.getsizeof(lst):,} bytes")  # ~800,000 bytes

# 生成器表达式：只是一个"配方"，几乎不占内存
gen = (x ** 2 for x in range(100_000))
print(f"生成器: {sys.getsizeof(gen):,} bytes")  # ~120 bytes

# 对 10 亿级别数据也是如此——生成器表达式不受影响
gen_big = (x ** 2 for x in range(10**9))  # 完全没问题
# lst_big = [x ** 2 for x in range(10**9)]  # 内存装不下
```

**案例2：作为函数唯一参数使用时省略括号**

```python
# 完整写法
total = sum((x for x in range(100) if x % 2 == 0))

# 省略括号——更简洁
total = sum(x for x in range(100) if x % 2 == 0)

# 其他常见用法
max_len = max(len(w) for w in ["apple", "banana", "cherry"])
any_ok = any(x > 0 for x in [1, 3, 5])       # 短路求值
all_ok = all(x > 0 for x in [1, -3, 5])      # 短路！遇到 -3 就停
joined = ", ".join(w.upper() for w in ["a", "b", "c"])
```

**案例3：生成器表达式只能迭代一次**

```python
gen = (x ** 2 for x in range(5))
print(list(gen))  # [0, 1, 4, 9, 16]
print(list(gen))  # []  ← 已耗尽！和列表推导式不同

# 如果需要多次使用，先用 list() 或 tuple() 收集起来
gen = (x ** 2 for x in range(5))
collected = list(gen)  # 收集到列表里，之后可多次使用
```

**案例4（工业级）：流式处理大数据——按批次消费生成器**

```python
import itertools

def batch(iterable, size):
    """惰性分批——一次只产出 size 个元素"""
    it = iter(iterable)
    while True:
        chunk = list(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk

# 从生成器表达式创建数据流（惰性，不占内存）
data_stream = (x ** 2 for x in range(10_000_000))

# 分批次处理，每批 1000 条——内存中始终只有 1000 条
total = 0
for chunk in batch(data_stream, 1000):
    total += sum(chunk)
print(f"总计: {total}")
```

---

## 7.5 四种推导式全览与选择指南

```
┌─────────────────────────────────────────────────────────┐
│  类型         语法              返回      求值    用途   │
├─────────────────────────────────────────────────────────┤
│  列表推导式   [x for x in it]    list      立即    收集  │
│  字典推导式   {k:v for k,v in it} dict     立即    映射  │
│  集合推导式   {x for x in it}    set       立即    去重  │
│  生成器表达式 (x for x in it)    generator 惰性    流式  │
└─────────────────────────────────────────────────────────┘
```

**选择流程图**：

```
需要什么容器？
  ├── list（需要索引/切片/多次迭代）→ 列表推导式 [...]
  ├── dict（键值映射）                → 字典推导式 {k:v for...}
  ├── set（去重/集合运算）            → 集合推导式 {x for...}
  └── 只迭代一次 + 数据可能很大       → 生成器表达式 (...)
```

---

## 本章速查

| 类型 | 语法 | 何时用 |
|------|------|--------|
| 列表 | `[x for x in it if cond]` | 需要 list（索引、多次遍历） |
| 字典 | `{k: v for k, v in it}` | 构建或变换映射 |
| 集合 | `{x for x in it}` | 去重、集合运算 |
| 生成器 | `(x for x in it)` | 大文件、流式数据、惰性求值 |

| 规则 | 说明 |
|------|------|
| for 后的 if | 过滤（无 else），筛掉元素 |
| for 前的 if | 变换（必须有 else），每个元素都保留 |
| 超过 2 层嵌套 | 拆成 for 循环 |
| 唯一参数时 | 生成器表达式可省略括号 `sum(x for x in data)` |
