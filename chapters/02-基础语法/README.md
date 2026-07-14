# 第二章：基础语法

---

## 2.1 变量与赋值

### 理论：变量不是"盒子"，是"标签"

很多语言把变量解释为"装数据的盒子"，但 Python 不这样。Python 的变量是贴在对象上的**标签（引用）**。

```
x = [1, 2, 3]
```

这行的意思是：
1. 先在内存中创建一个列表对象 `[1, 2, 3]`
2. 把标签 `x` 贴在这个对象上

**关键推论**：

- 一个对象可以有多个标签：`a = x` 表示给同一个对象多贴一个标签
- 如果对象被修改（可变对象），通过任何标签看到的内容都变了
- 如果只是换标签（重新赋值），源对象不受影响

**类比**：你有一个快递包裹（对象），上面可以贴多个收件人标签。包裹里的东西变了，所有收件人都看到变化。但如果一个新收件人把标签撕下来贴到另一个包裹上，原包裹不受影响。

---

### 关键字/语法

| 关键字 | 作用 |
|--------|------|
| `=` | 将变量名绑定到对象（不是复制！） |
| `is` | 判断两个变量是否指向**同一个对象**（比 id） |
| `==` | 判断两个对象的值是否**相等**（调 `__eq__`） |
| `id(x)` | 返回对象的内存地址（唯一标识） |
| `del x` | 删除变量（减少一次引用计数） |
| `None` | 表示"没有值"的唯一单例对象 |

---

### 案例

**案例1：`=` 不是复制，是多贴一个标签**

```python
a = [1, 2, 3]
b = a                    # b 和 a 是同一个对象的两个标签

b.append(4)
print(a)                 # [1, 2, 3, 4] —— "a"也变了！
print(a is b)            # True —— 同一个对象
```

**案例2：重新赋值是"换标签"，不是"改内容"**

```python
a = [1, 2, 3]
b = a
a = [4, 5, 6]            # a 换了标签，指向新列表
print(a)                  # [4, 5, 6]
print(b)                  # [1, 2, 3] —— b 还贴在原对象上
```

**案例3：可变默认参数的陷阱（面试高频题）**

```python
# ❌ 默认参数 [] 只在函数定义时创建一次
def bad_append(item, target=[]):
    target.append(item)
    return target

print(bad_append(1))  # [1]
print(bad_append(2))  # [1, 2] ← 同一个列表！

# ✅ 正确：用 None + 内部初始化
def good_append(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

---

## 2.2 基本数据类型

### 理论：四种基本类型及其特点

| 类型 | 示例 | 可变？ | 特别说明 |
|------|------|--------|----------|
| `int` | `42`, `-7`, `2**1000` | 不可变 | 任意精度，永远不会溢出 |
| `float` | `3.14`, `-0.5` | 不可变 | IEEE 754 双精度，**有精度误差** |
| `bool` | `True`, `False` | 不可变 | 是 `int` 的子类（True=1, False=0） |
| `NoneType` | `None` | 单例 | 表示"没值"，永远用 `is` 判断 |

**浮点数精度问题是理解 float 的关键**：

`0.1` 在十进制是精确的，但在二进制中是一个无限循环小数（就像十进制的 1/3 = 0.33333...），计算机只能截断存储，导致 `0.1 + 0.2 != 0.3`。

**类比**：用十进制小数精确表示 1/3 是不可能的，你只能写 0.3333（近似）。浮点数同理，只是换成了二进制表示。

---

### 关键字/语法

| 关键字 | 作用 |
|--------|------|
| `True` / `False` | 布尔字面量 |
| `None` | 空值单例 |
| `type(x)` | 查看变量类型 |
| `isinstance(x, type)` | 类型检查（推荐用这个，支持继承） |
| `math.isclose(a, b)` | 安全比较两个 float（带容差） |

---

### 案例

**案例1：int 的任意精度——永远不会溢出**

```python
big = 2 ** 1000
print(f"2^1000 的位数: {len(str(big))}")  # 302 位

# 对比：C 语言的 long long 最大只有 9.22×10^18
print(f"long long 最大值: {2**63 - 1:,}")
print(f"Python 轻松超过: {2**100:,}")     # 无压力
```

**案例2：浮点数的经典"bug"和正确比较方式**

```python
print(0.1 + 0.2)                 # 0.30000000000000004
print(0.1 + 0.2 == 0.3)          # False！

# ✅ 正确比较
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True
```

**案例3：金融计算用 Decimal 或整数（分），不用 float**

```python
from decimal import Decimal

# ❌ 用 float 做金额 → 精度丢失
price = 19.99
tax = 0.13
print(price * tax)  # 2.5987000000000002

# ✅ 用 Decimal → 精确
price = Decimal("19.99")
tax = Decimal("0.13")
print(price * tax)  # 2.5987 —— 精确！

# 另一种方案：用"分"做单位（整数运算）
price_cents = 1999     # 19.99元 = 1999分
tax_cents = int(1999 * 0.13)
print(f"{price_cents + tax_cents}分")  # 全部用整数，没有精度问题
```

---

## 2.3 字符串 (str)

### 理论：字符串是不可变的 Unicode 序列

Python 3 中，所有字符串都是 **Unicode**，天然支持中文、emoji 等。字符串是**不可变的**——任何"修改"操作实际上都是创建一个新字符串。

**类比**：字符串像刻在石板上的字，不能擦改。想改内容？只能重新刻一块石板。

---

### 关键字/语法

**创建字符串**：

```python
'hello'         # 单引号
"hello"         # 双引号（和单引号没区别）
'''三引号'''    # 可跨多行
r"raw\nstring"  # r 前缀：\n 不转义，保留原始字符
f"{变量}"       # f 前缀：格式化字符串（Python 3.6+）
```

**索引和切片**：

| 语法 | 含义 |
|------|------|
| `s[i]` | 第 i 个字符（0 开始，负数从末尾倒推） |
| `s[start:end]` | 从 start 到 end-1 的子串 |
| `s[start:end:step]` | 带步长的切片 |
| `s[::-1]` | 反转字符串 |

**常用方法（都不修改原字符串，返回新的）**：

| 方法 | 作用 |
|------|------|
| `s.split(sep)` | 按分隔符拆成列表 |
| `sep.join(list)` | 用分隔符拼接列表 |
| `s.strip()` | 去掉首尾空白 |
| `s.replace(old, new)` | 替换子串 |
| `s.find(sub)` | 查找子串，找不到返 -1（不抛异常） |
| `s.startswith(prefix)` | 以...开头？ |
| `s.upper()` / `s.lower()` | 全大写/全小写 |

**格式化（三种方式，推荐 f-string）**：

```python
name = "Alice"; age = 30
"%s, %d" % (name, age)           # % 格式化（旧式）
"{} {}".format(name, age)         # format 方法
f"{name} {age}"                   # f-string（推荐）
```

---

### 案例

**案例1：切片——理解左闭右开 [start, end)**

```python
text = "Python编程"
# 正索引: P=0, y=1, t=2, h=3, o=4, n=5, 编=6, 程=7
# 负索引: P=-8, y=-7, t=-6, h=-5, o=-4, n=-3, 编=-2, 程=-1

print(text[0:6])       # Python  [0, 6)
print(text[6:8])       # 编程
print(text[-2:])       # 编程    从-2到末尾
print(text[::-1])      # 程编nohtyP  反转
print(text[::2])       # Pto编   隔一个取一个
```

**案例2：split 和 join 是互逆操作**

```python
text = "apple,banana,orange"
parts = text.split(",")             # ['apple', 'banana', 'orange']
back = ",".join(parts)              # "apple,banana,orange"

# 限制切割次数
path = "/usr/local/bin/python"
print(path.split("/", maxsplit=2))  # ['', 'usr', 'local/bin/python']
```

**案例3：f-string 格式规范微语言**

```python
n = 1234567.89
print(f"{n:,.2f}")       # 1,234,567.89  —— 千位分隔+2位小数
print(f"{n:.2e}")        # 1.23e+06      —— 科学计数法
print(f"{0.865:.1%}")    # 86.5%         —— 百分比

name = "Bob"
print(f"|{name:<10}|")   # |Bob       |  —— 左对齐，宽度10
print(f"|{name:>10}|")   # |       Bob|  —— 右对齐
print(f"|{name:^10}|")   # |   Bob    |  —— 居中
print(f"|{name:*^10}|")  # |***Bob****|  —— *填充居中
```

---

## 2.4 运算符

### 理论：运算符的优先级和短路求值

**算术运算符**：`+ - * / // % **`（`**` 优先级最高，`//` 是整除，`/` 总是返回 float）

**逻辑运算符**：`and` `or` `not`
- **短路求值**：`a and b`，如果 a 是 False，b 根本不会执行；`a or b`，如果 a 是 True，b 不会执行
- 返回的是**被求值的那个对象本身**，不一定是 True/False

**海象运算符** `:=`（Python 3.8+）：在表达式中做赋值，一步完成"取值 + 判断"。

---

### 案例

**案例1：短路求值的实用场景**

```python
# 安全取值：如果 user 是 None，不会执行 user.get("name")
user = None
name = user and user.get("name")   # 返回 None，user.get 没执行

# 提供默认值：第一个为 Falsy 时用第二个
display_name = name or "匿名用户"   # "匿名用户"

# 注意：or 对 0 和空字符串也会走默认值！
count = 0
print(count or "无数据")            # "无数据" —— 可能不是你想要的
```

**案例2：海象运算符——if 中一步完成赋值和判断**

```python
import re

# ❌ 传统：赋值和判断分两步，代码重复
match = re.search(r"\d+", "ID: 12345")
if match:
    print(match.group())

# ✅ 海象：一步完成
if (match := re.search(r"\d+", "ID: 12345")):
    print(match.group())
```

**案例3：逐行读文件——海象运算符的经典用法**

```python
# ❌ 传统：需要先读一行，再循环
line = f.readline()
while line:
    process(line)
    line = f.readline()

# ✅ 海象：读和判断一步完成
while (line := f.readline()):
    process(line)
```

---

## 本章速查

| 概念 | 核心理解 |
|------|----------|
| 变量 | 不是盒子，是贴在对象上的标签 |
| `is` | 判断是不是同一个对象（比 id） |
| `==` | 判断值是否相等（调 `__eq__`） |
| int | 任意精度，永不溢出 |
| float | 有精度误差，用 `math.isclose` 比较，金额用 Decimal |
| str | 不可变 Unicode，索引切片都返回新字符串 |
| `and`/`or` | 短路求值，返回被求值对象 |
| `:=` | 表达式内赋值，if/while 中一步完成取值+判断 |
