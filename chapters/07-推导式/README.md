# 第七章：推导式

---

## 理论：推导式就是把 for 循环写成一行

推导式是 Python 从数学集合论借来的语法。数学中你可以写：

> { x² | x ∈ {1,2,3,4,5}, x 是偶数 }

Python 中你写：

```python
{x**2 for x in [1,2,3,4,5] if x % 2 == 0}
```

**四种推导式**：方括号 = list，花括号+冒号 = dict，花括号 = set，圆括号 = generator。

**什么时候用推导式？** 当你对一个集合"做映射"或"做过滤"时。如果逻辑超过两行，就拆成 for 循环。

---

## 关键字/语法

**推导式的通用结构**：

```python
[表达式 for 变量 in 数据源 if 条件]
```

**关键规则**：

| 写法 | 含义 | 示例 |
|------|------|------|
| `if` 在 `for` **后面** | **过滤器**：滤掉不满足的 | `[x for x in nums if x > 0]` |
| `if-else` 在 `for` **前面** | **变换器**：每个都保留，值可能变 | `["正" if x>0 else "负" for x in nums]` |

**铁律**：for 后的 if 没有 else（它是过滤），for 前的 if 必须有 else（它是变换，每个元素都要有结果）。

**四种推导式语法**：

```python
[x for x in it]              # 列表推导式 → list（立即求值）
{x for x in it}              # 集合推导式 → set（立即求值）
{k: v for k, v in it}        # 字典推导式 → dict（立即求值）
(x for x in it)              # 生成器表达式 → generator（惰性求值）
```

---

## 案例

**案例1：从 for 循环到推导式的演变**

```python
# for 循环写法（4行）
squares = []
for i in range(10):
    if i % 2 == 0:
        squares.append(i ** 2)

# 推导式写法（1行）
squares = [i ** 2 for i in range(10) if i % 2 == 0]
# [0, 4, 16, 36, 64]
```

**案例2：if 在 for 后（过滤）vs if-else 在 for 前（变换）**

```python
nums = [1, 2, 3, 4, 5, 6]

# 过滤：丢掉所有不满足条件的 → 结果元素变少
evens = [x for x in nums if x % 2 == 0]
print(evens)  # [2, 4, 6]

# 变换：每个元素都保留，但值根据条件改变 → 结果元素数不变
labels = ["偶数" if x % 2 == 0 else "奇数" for x in nums]
print(labels)  # ['奇数', '偶数', '奇数', '偶数', '奇数', '偶数']
```

**案例3：字典推导式——键值互换、过滤、构建**

```python
# 键值互换
d = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in d.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}

# 带过滤的字典构建
scores = {"Alice": 85, "Bob": 92, "Charlie": 78}
passed = {name: score for name, score in scores.items() if score >= 80}
print(passed)  # {'Alice': 85, 'Bob': 92}
```

**案例4：嵌套推导式——展平二维列表**

```python
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# 展平（双层 for 的顺序 = 普通 for 循环的嵌套顺序）
flat = [x for row in matrix for x in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 等价于：
flat = []
for row in matrix:       # 外层
    for x in row:          # 内层
        flat.append(x)
```

**案例5（工业级）：数据清洗——多个推导式串联**

```python
# 清洗手机号列表
raw_phones = ["138-1234-5678", "  ", "abc", "15912345678"]

# 步骤1：去除非数字，过滤空值
cleaned = [re.sub(r"\D", "", p) for p in raw_phones if p.strip()]
# 步骤2：过滤长度不对的
valid = [p for p in cleaned if len(p) == 11 and p.startswith("1")]

print(valid)  # ['13812345678', '15912345678']
```

---

## 本章速查

```
方括号 [x for...]  → list（立即）
圆括号 (x for...)  → generator（惰性）
花括号 {x for...}  → set（去重）
花括号 {k:v for...} → dict

铁律：for 后的 if 是过滤器（无 else），for 前的 if 是变换器（必须有 else）
```
