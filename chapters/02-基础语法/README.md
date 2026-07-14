# 第二章：基础语法

---

## 2.1 变量与赋值

### 理论：变量不是"盒子"，是"标签"

```python
x = [1, 2, 3]
```

这行代码实际做了两件事：
1. 在内存中创建立一个列表对象 `[1, 2, 3]`
2. 把标签 `x` 贴在这个对象上

**类比**：快递包裹（= 对象），上面贴收件人标签（= 变量名）。包裹里的东西变了 → 所有收件人都看到变化。标签撕下来贴到另一个包裹上 → 原包裹不受影响。

**关键推论**：
- `a = b` 表示给同一个对象多贴一个标签（不是复制！）
- 修改可变对象内容 → 所有引用它的变量都"看到"变化
- 重新赋值（`=`）→ 只是换标签指向新对象，原对象不受影响

---

### 关键字/语法

| 关键字/函数 | 作用 | 示例 |
|------------|------|------|
| `=` | 将变量绑定到对象（不是复制） | `x = 42` |
| `is` | 判断是否指向**同一个对象**（比 id） | `a is b` |
| `==` | 判断**值**是否相等（调用 `__eq__`） | `a == b` |
| `id(x)` | 返回对象的唯一标识（CPython 中是内存地址） | `id(x)` |
| `type(x)` | 查看对象的类型 | `type(42)` → `<class 'int'>` |
| `isinstance(x, t)` | 检查 x 是否是 t 类型（**推荐**，支持继承） | `isinstance(42, int)` |
| `del x` | 删除变量引用（引用计数 -1） | `del x` |
| `None` | 表示"没有值"的**唯一单例对象**，永远用 `is` 判断 | `x is None` |

---

### 案例

**案例1：`=` 不是复制——`is` vs `==` 的区别**

```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)    # True  —— 值相同
print(a is b)    # False —— 不同的对象！
print(a is c)    # True  —— 同一个对象

# 用 id 验证
print(f"a 的 id: {id(a)}")
print(f"b 的 id: {id(b)}")   # 和 a 不同
print(f"c 的 id: {id(c)}")   # 和 a 相同
```

**案例2：重新赋值是"换标签"，不是"改内容"**

```python
a = [1, 2, 3]
b = a              # b 贴在同一个对象上
a = [4, 5, 6]      # a 换了标签，指向新对象

print(a)  # [4, 5, 6]
print(b)  # [1, 2, 3]  —— b 还贴在原对象上，没受影响

# 对比：原地修改（真正影响 b）
a = [1, 2, 3]
b = a
a.append(4)        # 修改同一个对象的内容
print(b)           # [1, 2, 3, 4]  —— b 也看到了变化
```

**案例3：type() vs isinstance()——为什么推荐 isinstance**

```python
print(type(42) == int)              # True —— 严格类型判断

# isinstance 支持继承关系
class MyInt(int):
    pass

x = MyInt(42)
print(type(x) == int)               # False —— type 不支持子类
print(isinstance(x, int))           # True  —— isinstance 支持继承

# 一次检查多种类型
print(isinstance("hello", (int, str)))  # True
```

**案例4（面试陷阱）：可变默认参数**

```python
# ❌ 默认参数只在函数定义时求值一次！
def bad(item, target=[]):
    target.append(item)
    return target

print(bad(1))  # [1]
print(bad(2))  # [1, 2]  ← 同一个列表！上次的 1 还在

# ✅ 正确：用 None，调用时再创建
def good(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target

print(good(1))  # [1]
print(good(2))  # [2]  ← 每次都是新列表
```

---

## 2.2 基本数据类型

### 理论：四种基础类型

| 类型 | 示例 | 可变？ | 关键点 |
|------|------|--------|--------|
| `int` | `42`, `2**1000` | 不可变 | **任意精度**，永不溢出 |
| `float` | `3.14` | 不可变 | IEEE 754 双精度，**有精度误差** |
| `bool` | `True`, `False` | 不可变 | **是 int 的子类**（True=1, False=0） |
| `NoneType` | `None` | 单例 | 表示"没值"，永远用 `is None` |

**浮点数精度问题**的核心原因：十进制 `0.1` 在二进制中是无限循环小数（如同十进制的 1/3 = 0.3333...），计算机只能截断存储 → 近似值 → `0.1 + 0.2 ≠ 0.3`。

---

### 知识点详解

**int——任意精度整数**：

Python 的 int 底层用变长数组存储数字，理论上只受内存限制，永远不会溢出。

```python
# 可以用 _ 分隔数字，提高可读性
billion = 1_000_000_000

# 进制表示
bin_num = 0b1010      # 二进制 → 10
oct_num = 0o755       # 八进制 → 493
hex_num = 0xFF        # 十六进制 → 255
```

**float——IEEE 754 双精度**：

Python float 对应 C 语言的 double，64 位存储。有效位数约 15-17 位十进制。

```python
# 特殊值
float("inf")      # 正无穷
float("-inf")     # 负无穷
float("nan")      # Not a Number

# 判断 NaN（NaN 不等于任何值，包括自己）
import math
print(math.isnan(float("nan")))   # True
```

**bool——int 的子类**：

```python
print(True == 1)      # True
print(False == 0)     # True
print(True + True)    # 2  —— 因为 True 就是 1
print(isinstance(True, int))  # True —— bool 是 int 的子类
```

---

### 案例

**案例1：int 任意精度——做其他语言做不到的事**

```python
# 计算 2 的 1000 次方
big = 2 ** 1000
print(f"2^1000 = {big}")                  # 一个 302 位的数字
print(f"位数: {len(str(big))}")           # 302

# C 语言 long long 最大约 9.22×10^18
# Python 可以轻松超过
print(f"2^100 = {2**100:,}")              # 无压力

# 大数阶乘
import math
print(f"100! 的位数: {len(str(math.factorial(100)))}")  # 158 位
```

**案例2：浮点数的精度问题和正确处理**

```python
# 经典的"bug"
print(0.1 + 0.2)                 # 0.30000000000000004
print(0.1 + 0.2 == 0.3)          # False

# ✅ 正确比较：用 math.isclose
import math
print(math.isclose(0.1 + 0.2, 0.3))          # True
print(math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-15))  # True（指定容差）

# 查看浮点数的精确十进制值
import decimal
print(decimal.Decimal(0.1))
# 0.1000000000000000055511151231257827021181583404541015625
# 👆 这就是 0.1 在计算机内部的真实值！
```

**案例3：金融计算——用 Decimal 或整数（分）**

```python
from decimal import Decimal

# ❌ float 做金额：精度丢失
print(19.99 * 0.13)           # 2.5987000000000002

# ✅ Decimal：精确
price = Decimal("19.99")
tax_rate = Decimal("0.13")
print(price * tax_rate)       # 2.5987 —— 精确！

# ✅ 另一种方案：整数运算，以"分"为单位
price_cents = 1999            # 19.99 元 = 1999 分
tax_cents = int(1999 * 0.13)  # 税额也以分计
total_cents = price_cents + tax_cents
print(f"{total_cents // 100}.{total_cents % 100:02d} 元")  # 无浮点误差
```

**案例4：真值测试——哪些值是 False**

```python
# Python 中只有这 8 种值是 False
falsy = [False, None, 0, 0.0, 0j, "", [], {}, set(), (), range(0)]

for v in falsy:
    print(f"{repr(v):>15} → {bool(v)}")    # 全部是 False

# 其余都是 True
print(bool(-1))         # True
print(bool(" "))        # True（空格 ≠ 空字符串！）
print(bool([None]))     # True（非空列表）
```

---

## 2.3 字符串 (str)

### 理论：不可变的 Unicode 序列

Python 3 中所有字符串都是 **Unicode**，天然支持中文、emoji。字符串是**不可变的**——任何"修改"操作实际是创建新字符串。

---

### 知识点详解

**创建字符串的多种方式**：

```python
'hello'          # 单引号
"hello"          # 双引号——和单引号没区别
'''三引号'''     # 可跨多行
"""三引号"""     # 同上
r"raw\nstring"   # r 前缀：\n 不转义，保持原始字符
b"bytes"         # b 前缀：字节串
f"{变量}"        # f 前缀：格式化字符串（Python 3.6+）
```

**索引和切片——左闭右开 [start, end)**：

```python
s = "Python编程"
# 正索引: P=0 y=1 t=2 h=3 o=4 n=5 编=6 程=7
# 负索引: P=-8 y=-7 t=-6 h=-5 o=-4 n=-3 编=-2 程=-1

s[0]       # 'P'      —— 单个字符
s[-1]      # '程'     —— 最后一个
s[0:6]     # 'Python' —— [0, 6)，不包含6
s[6:]      # '编程'   —— 从6到末尾
s[::-1]    # '程编nohtyP' —— 反转（步长-1）
s[::2]     # 'Pto编'  —— 每隔一个取
```

**字符串常用方法（全都不修改原字符串，返回新的）**：

| 方法 | 作用 | 示例 |
|------|------|------|
| `s.split(sep)` | 按分隔符拆成列表 | `"a,b".split(",")` → `["a","b"]` |
| `s.rsplit(sep, n)` | 从右边开始分割 n 次 | `"a.b.c".rsplit(".",1)` → `["a.b","c"]` |
| `sep.join(list)` | 用分隔符拼接 | `",".join(["a","b"])` → `"a,b"` |
| `s.strip(chars)` | 去掉首尾字符（默认空白） | `" hi ".strip()` → `"hi"` |
| `s.replace(old, new, n)` | 替换（可选限制次数） | `"aab".replace("a","x",1)` → `"xab"` |
| `s.find(sub)` | 查子串位置，**找不到返 -1** | `"abc".find("z")` → `-1` |
| `s.index(sub)` | 查子串位置，找不到**抛异常** | — |
| `s.count(sub)` | 统计子串出现次数 | `"aba".count("a")` → `2` |
| `s.startswith(pre)` | 以...开头？ | `"abc".startswith("a")` |
| `s.endswith(suf)` | 以...结尾？ | `"abc.py".endswith(".py")` |
| `s.upper()` | 全大写 | `"abc".upper()` → `"ABC"` |
| `s.lower()` | 全小写 | — |
| `s.isdigit()` | 是否全是数字 | `"123".isdigit()` → True |
| `s.isalpha()` | 是否全是字母 | — |
| `s.isalnum()` | 是否全是字母或数字 | — |

**字符串格式化——三种方式演进**：

```python
name = "Alice"; age = 30

# 方式1：% 格式化（Python 2 风格，不推荐）
"%s 今年 %d 岁" % (name, age)

# 方式2：str.format()（Python 3 引入）
"{} 今年 {} 岁".format(name, age)
"{n} 今年 {a} 岁".format(n=name, a=age)

# 方式3：f-string（Python 3.6+，推荐！）
f"{name} 今年 {age} 岁"
f"{name} 明年 {age + 1} 岁"    # 支持任意表达式
```

---

### 案例

**案例1：切片——左闭右开 [start, end)**

```python
text = "Python编程"

print(text[0:6])      # Python  —— 索引 0 到 5
print(text[6:8])      # 编程    —— 索引 6 到 7
print(text[-2:])      # 编程    —— 从 -2 到末尾
print(text[:6])       # Python  —— 省略 start，从 0 开始
print(text[6:])       # 编程    —— 省略 end，到末尾
print(text[::-1])     # 程编nohtyP ——反转
print(text[::2])      # Pto编   —— 每 2 个字符取一个
print(text[1:6:2])    # yhn     —— 索引 1-5，步长 2
```

**案例2：split 和 join 的互逆关系**

```python
# split：拆开
text = "apple,banana,orange"
parts = text.split(",")
print(parts)  # ['apple', 'banana', 'orange']

# join：拼回
print(",".join(parts))   # "apple,banana,orange"
print(" | ".join(parts)) # "apple | banana | orange"

# 限制 split 次数
path = "/usr/local/bin/python"
print(path.split("/", maxsplit=2))
# ['', 'usr', 'local/bin/python']  —— 只拆了前两个 /

# rsplit：从右边开始拆
print(path.rsplit("/", maxsplit=1))
# ['/usr/local/bin', 'python']  —— 取文件名很有用
```

**案例3：f-string 格式规范微语言**

```python
n = 1234567.89

print(f"{n:.2f}")        # 1234567.89   保留 2 位小数
print(f"{n:,.2f}")       # 1,234,567.89 千位分隔
print(f"{n:.2e}")        # 1.23e+06     科学计数法
print(f"{0.865:.1%}")    # 86.5%        百分比

# 对齐和填充
name = "Bob"
print(f"|{name:<10}|")   # |Bob       |  左对齐
print(f"|{name:>10}|")   # |       Bob|  右对齐
print(f"|{name:^10}|")   # |   Bob    |  居中
print(f"|{name:*^10}|")  # |***Bob****|  * 填充居中

# 数字的进位和补零
print(f"{42:05d}")       # 00042        补零到 5 位
print(f"{255:b}")        # 11111111     二进制
print(f"{255:x}")        # ff           十六进制
```

**案例4（工业级）：安全的字符串截断（支持中文）**

```python
def truncate(text: str, max_len: int, suffix: str = "...") -> str:
    """截断字符串，正确处理中文等多字节字符"""
    if len(text) <= max_len:
        return text
    return text[:max_len - len(suffix)] + suffix

print(truncate("Hello, World!", 10))      # Hello, W...
print(truncate("你好世界Python编程", 8))   # 你好世界P...
```

---

## 2.4 运算符

### 理论

**算术运算符**（按优先级从高到低）：

`**`（幂） > `-`（负号） > `* / // %` > `+ -`

**比较运算符**：`== != > < >= <=`；Python 支持**链式比较** `0 < x < 10`。

**逻辑运算符** `and` `or` `not`：
- **短路求值**：`a and b`，a 为 False 则 b 不执行；`a or b`，a 为 True 则 b 不执行
- 返回的是**被求值对象本身**，不一定是 True/False

**海象运算符 `:=`**（Python 3.8+）：表达式内赋值，一步完成"取值 + 判断"。

**位运算符** `& | ^ ~ << >>`：对整数的二进制位进行操作。

---

### 案例

**案例1：短路求值——安全取值和默认值**

```python
# 安全取值：user 为 None 时不会调用 .get()
user = None
name = user and user.get("name")    # 返回 None，不抛异常

# 默认值：第一个 Falsy 时用第二个
display = name or "匿名用户"         # "匿名用户"

# ⚠️ 注意：or 对 0、空字符串也会走默认值
count = 0
print(count or "无数据")             # "无数据" —— 可能不是你想要的

# ✅ 更精确的做法：明确判断 None
count if count is not None else "无数据"
```

**案例2：海象运算符——避免重复计算**

```python
import re

# ❌ 传统：调用两次 re.search，或者多写一行
text = "ID: 12345"
match = re.search(r"\d+", text)
if match:
    print(match.group())

# ✅ 海象：赋值+判断一步完成
if (match := re.search(r"\d+", text)):
    print(match.group())

# 逐行读文件——海象的经典场景
# while (line := f.readline().strip()):
#     process(line)
```

**案例3：位运算——权限标志位的实战用法**

```python
# 用位运算表示和检查权限（比多个 bool 变量更高效）
READ = 0b001     # 1
WRITE = 0b010    # 2
EXECUTE = 0b100  # 4

# 设置权限（用 | 组合）
my_perm = READ | WRITE   # 0b011 = 3
print(f"权限值: {my_perm}")  # 3

# 检查权限（用 & 检查）
has_read = (my_perm & READ) != 0      # True
has_exec = (my_perm & EXECUTE) != 0   # False
print(f"可读: {has_read}, 可执行: {has_exec}")

# 添加权限（用 |=）
my_perm |= EXECUTE
# 移除权限（用 &= ~）
my_perm &= ~WRITE
```

---

## 2.5 类型转换

### 知识点

| 函数 | 做什么 | 示例 |
|------|--------|------|
| `int(x)` | 转整数 | `int("42")` → 42, `int(3.9)` → 3（截断） |
| `float(x)` | 转浮点 | `float("3.14")` → 3.14 |
| `str(x)` | 转字符串 | `str(42)` → "42" |
| `bool(x)` | 转布尔 | `bool([])` → False |
| `list(x)` | 转列表 | `list("abc")` → ["a","b","c"] |
| `tuple(x)` | 转元组 | `tuple([1,2])` → (1,2) |
| `set(x)` | 转集合 | `set([1,1,2])` → {1,2} |
| `chr(n)` | Unicode 码 → 字符 | `chr(65)` → "A" |
| `ord(c)` | 字符 → Unicode 码 | `ord("A")` → 65 |

```python
# int() 的第二个参数：指定进制
print(int("FF", 16))    # 255  —— 十六进制转十进制
print(int("1010", 2))   # 10   —— 二进制转十进制
print(bin(10))          # '0b1010' —— 十进制转二进制字符串
print(hex(255))         # '0xff'
print(oct(8))           # '0o10'
```

---

## 本章速查

| 概念 | 核心理解 |
|------|----------|
| 变量 | 不是盒子，是贴在对象上的标签 |
| `is` vs `==` | is 比 id（同一对象？），== 比值（相等？） |
| int | 任意精度，永不溢出 |
| float | 有精度误差；用 `math.isclose` 比较；金额用 Decimal 或整数(分) |
| bool | int 的子类，True=1, False=0 |
| str | 不可变 Unicode；切片左闭右开；f-string 最推荐 |
| `and`/`or` | 短路求值；返回被求值对象 |
| `:=` | 表达式内赋值（Python 3.8+） |
