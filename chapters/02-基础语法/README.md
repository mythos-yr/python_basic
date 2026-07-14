# 第二章：基础语法

---

## 2.1 变量与基本数据类型

### 知识点：变量的本质——名字到对象的引用

Python 中的变量不是"盒子"，而是贴在对象上的**标签**。理解这一点至关重要。

**案例1：用 id() 证明变量是引用**

```python
# 变量只是一个名字，指向内存中的对象
a = [1, 2, 3]
b = a                    # b 和 a 指向同一个对象

print(f"a 的 id: {id(a)}")
print(f"b 的 id: {id(b)}")
print(f"a is b: {a is b}")   # True — 同一个对象

b.append(4)
print(f"a = {a}")             # [1, 2, 3, 4] — a 也变了！
print(f"b = {b}")             # [1, 2, 3, 4]
```

**案例2：重新赋值 vs 原地修改**

```python
# 重新赋值：换标签，指向新对象
x = [1, 2, 3]
y = x
x = [4, 5, 6]            # x 指向了新列表
print(f"x = {x}")        # [4, 5, 6]
print(f"y = {y}")        # [1, 2, 3] — y 还是指向旧列表

# 原地修改：修改的是同一个对象
x = [1, 2, 3]
y = x
x.append(4)              # 修改原有对象的内容
print(f"x = {x}")        # [1, 2, 3, 4]
print(f"y = {y}")        # [1, 2, 3, 4] — y 也被"影响"了
```

**案例3：工业级——参数传递中可变对象的陷阱与防御**

```python
from copy import deepcopy
from typing import List, Optional

class UserService:
    """
    用户服务类。展示如何在方法中安全地处理可变默认参数，
    避免多个调用之间的状态泄露。
    """

    def __init__(self):
        self._cache = {}

    # ❌ 错误做法：可变默认参数在函数定义时只创建一次
    # def add_tags(self, user_id: int, tags: List[str] = []):

    # ✅ 正确做法：默认值用 None，内部再初始化
    def add_tags(self, user_id: int, tags: Optional[List[str]] = None):
        if tags is None:
            tags = []

        if user_id not in self._cache:
            self._cache[user_id] = []

        # ⚠️ 如果不复制，外部的修改会污染内部缓存
        self._cache[user_id].extend(deepcopy(tags))

    def get_tags(self, user_id: int) -> List[str]:
        # 返回值也要复制，防止外部修改内部缓存
        return deepcopy(self._cache.get(user_id, []))


# 演示默认参数的危险
def dangerous_append(item, target=[]):
    """这个函数的默认参数[]只会创建一次！"""
    target.append(item)
    return target

print(dangerous_append(1))   # [1]
print(dangerous_append(2))   # [1, 2] — 同一个列表！
print(dangerous_append(3))   # [1, 2, 3] — 持续累积！
```

---

### 知识点：int 类型——任意精度整数

Python 的 int 不会溢出，因为它底层用变长数组存储数字。

**案例1：超大整数运算**

```python
# Python 的 int 可以处理任意大的整数
big = 2 ** 1000
print(f"2^1000 = {big}")      # 一个300多位的数字
print(f"位数: {len(str(big))}")  # 302

# 同样可以处理大数运算
huge = 2 ** 10000
print(f"2^10000 的位数: {len(str(huge))}")  # 3011
```

**案例2：int 的内存占用**

```python
import sys

# 小整数
small = 42
print(f"42 占 {sys.getsizeof(small)} 字节")  # 28 字节

# 大整数
large = 2 ** 1000
print(f"2^1000 占 {sys.getsizeof(large)} 字节")  # 160 字节

# 对比：C 语言的 long long 最大约 9.22 × 10^18
print(f"long long 最大值: {2**63 - 1:,}")
# Python: 轻松超过这个值
print(f"Python: {2**100:,}")
```

**案例3：工业级——金融计算中的精确整数运算**

```python
from decimal import Decimal
from typing import Tuple

class Money:
    """
    用整数（分）存储金额，避免浮点数精度问题。
    金融系统中常见的做法。
    """

    def __init__(self, amount_in_cents: int):
        self.cents = amount_in_cents

    @classmethod
    def from_yuan(cls, yuan: str) -> "Money":
        """从元字符串创建（如 '19.99'）"""
        # 用 Decimal 避免浮点数精度问题
        d = Decimal(yuan)
        cents = int(d * 100)
        return cls(cents)

    def to_yuan(self) -> str:
        """转为元的字符串表示"""
        yuan = self.cents // 100
        fen = self.cents % 100
        return f"{yuan}.{fen:02d}"

    def __add__(self, other: "Money") -> "Money":
        return Money(self.cents + other.cents)

    def __mul__(self, factor: int) -> "Money":
        return Money(self.cents * factor)

    def split(self, parts: int) -> Tuple["Money", ...]:
        """均分金额，余数按顺序分配到前几份"""
        base = self.cents // parts
        remainder = self.cents % parts
        result = []
        for i in range(parts):
            if i < remainder:
                result.append(Money(base + 1))
            else:
                result.append(Money(base))
        return tuple(result)


# 演示：三人分 10 元
m = Money.from_yuan("10.00")
parts = m.split(3)
for i, p in enumerate(parts, 1):
    print(f"第{i}人: {p.to_yuan()}")
# 第1人: 3.34
# 第2人: 3.33
# 第3人: 3.33
```

---

### 知识点：float 类型——IEEE 754 双精度浮点数

浮点数在计算机中是以二进制形式近似存储的，这导致了经典的精度问题。

**案例1：浮点数的"经典迷惑"**

```python
# 这可能是 Python 中最让人困惑的输出之一
print(0.1 + 0.2)                # 0.30000000000000004
print(0.1 + 0.2 == 0.3)         # False！

# 为什么？因为 0.1 在二进制中是无限循环小数
# 就像 1/3 在十进制中是 0.3333... 无限循环一样

# 查看浮点数的精确表示
import struct
def float_to_hex(f):
    return struct.pack('d', f).hex()

print(f"0.1 在内存中: {float_to_hex(0.1)}")  # 只是一串近似值的字节
```

**案例2：正确比较浮点数的方式**

```python
import math
import sys

# ❌ 不要这样做
# if 0.1 + 0.2 == 0.3: ...

# ✅ 使用 math.isclose（相对容差 + 绝对容差）
print(math.isclose(0.1 + 0.2, 0.3))                    # True
print(math.isclose(0.1 + 0.2, 0.3, rel_tol=1e-15))     # True

# 自定义近似比较
def approx_equal(a, b, epsilon=1e-9):
    """判断两个浮点数是否足够接近"""
    return abs(a - b) < epsilon

print(approx_equal(0.1 + 0.2, 0.3))  # True
```

**案例3：工业级——科学计算中的浮点数陷阱处理**

```python
import math
from typing import List

class FloatAccumulator:
    """
    精确的浮点数累加器。
    使用 Kahan 求和算法补偿精度损失。
    在数值计算中避免大量累加带来的误差累积。
    """

    def __init__(self):
        self._sum = 0.0
        self._compensation = 0.0   # 补偿项：记录丢失的低位

    def add(self, value: float) -> None:
        """Kahan 求和：每次加法都补偿上一次的舍入误差"""
        y = value - self._compensation    # 用补偿值修正输入
        t = self._sum + y                  # 加法
        self._compensation = (t - self._sum) - y  # 计算丢失的低位
        self._sum = t

    @property
    def total(self) -> float:
        return self._sum

    @classmethod
    def compare_methods(cls, numbers: List[float]):
        """对比普通累加和 Kahan 累加的差异"""
        naive_sum = sum(numbers)
        acc = cls()
        for n in numbers:
            acc.add(n)
        print(f"普通 sum():    {naive_sum:.15f}")
        print(f"Kahan 累加:    {acc.total:.15f}")
        print(f"差异:          {abs(naive_sum - acc.total):.2e}")


# 测试：大量小数的累加
numbers = [0.1] * 10_000_000
# 理论上：0.1 × 1000万 = 100万
FloatAccumulator.compare_methods(numbers[:100])
# 普通 sum():    9.999999999999831
# Kahan 累加:    10.000000000000000
# 差异:          1.69e-13 ← 虽然单个误差极小，但累加后会放大
```

---

## 2.2 字符串 (str)

### 知识点：字符串不可变性

**案例1：验证不可变性**

```python
text = "hello"
# text[0] = "H"          # ❌ TypeError: 'str' object does not support item assignment

# 要修改字符串，只能创建新的
text = "H" + text[1:]    # 创建一个新字符串，变量重新指向它
print(text)               # "Hello"

# 每次"修改"都会产生新的字符串对象
s = "abc"
print(f"原始 id: {id(s)}")
s = s + "d"
print(f"修改后 id: {id(s)}")  # 不同的 id！
```

**案例2：索引与切片**

```python
text = "Python编程"

# 正索引:  P(0)  y(1)  t(2)  h(3)  o(4)  n(5)  编(6)  程(7)
# 负索引:  P(-8) y(-7) t(-6) h(-5) o(-4) n(-3) 编(-2) 程(-1)

print(text[0])       # P
print(text[-1])      # 程
print(text[0:6])     # Python   — [start:end) 左闭右开
print(text[6:8])     # 编程
print(text[:6])      # Python   — 省略 start，默认从0开始
print(text[6:])      # 编程     — 省略 end，默认到末尾
print(text[::-1])    # 程编nohtyP — 步长为-1，即反转

# 切片不会越界！
print(text[0:100])   # Python编程 — 自动截断，不报错
```

**案例3：工业级——安全的字符串截断（支持中文等多字节字符）**

```python
import textwrap
from typing import Optional

class StringUtil:
    """字符串工具类"""

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        安全截断字符串，正确处理 Unicode 字符（中文、emoji 等）。
        不破坏多字节字符的完整性。
        """
        if len(text) <= max_length:
            return text

        # 确保截断后加上后缀不超过最大长度
        trim_length = max_length - len(suffix)
        if trim_length <= 0:
            return suffix[:max_length]

        return text[:trim_length] + suffix

    @staticmethod
    def ellipsis_middle(text: str, max_length: int) -> str:
        """
        中间截断（常用于文件路径、URL 的显示）。
        例: "/very/long/path/to/file.txt" → "/very/.../file.txt"
        """
        if len(text) <= max_length:
            return text

        # 前后各保留一半（减去 "..." 的3个字符）
        half = (max_length - 3) // 2
        return text[:half] + "..." + text[-half:]

    @staticmethod
    def safe_unicode_trim(text: str, byte_limit: int, encoding: str = "utf-8") -> str:
        """
        按字节数截断，不切断多字节字符。
        用于适配数据库 VARCHAR(N) 等字节限制的场景。
        """
        encoded = text.encode(encoding)
        if len(encoded) <= byte_limit:
            return text

        # 逐字符减少，直到字节数满足要求
        while len(text.encode(encoding)) > byte_limit:
            text = text[:-1]
        return text


util = StringUtil()
print(util.truncate("Hello World", 8))                         # Hello...
print(util.truncate("你好世界Python", 8))                       # 你好世界P...
print(util.ellipsis_middle("/usr/local/lib/python3.11/site-packages/", 35))
# /usr/local/.../site-packages/
print(util.safe_unicode_trim("你好世界！", byte_limit=10))      # 你好世
```

---

### 知识点：字符串常用方法

**案例1：分割与合并**

```python
# split: 拆成列表
text = "apple,banana,orange"
parts = text.split(",")
print(parts)               # ['apple', 'banana', 'orange']

# 限制分割次数
text = "a,b,c,d,e"
print(text.split(",", maxsplit=2))  # ['a', 'b', 'c,d,e']

# rsplit: 从右边开始分割
path = "/usr/local/bin/python"
print(path.rsplit("/", maxsplit=1))  # ['/usr/local/bin', 'python']

# join: 用分隔符拼接列表
words = ["Python", "is", "awesome"]
print(" ".join(words))       # Python is awesome
print(",".join(words))       # Python,is,awesome
```

**案例2：查找与替换**

```python
text = "the quick brown fox jumps over the lazy dog"

# find: 查找子串位置，找不到返回 -1（不抛异常）
print(text.find("fox"))          # 16
print(text.find("cat"))          # -1

# index: 类似 find，但找不到会抛 ValueError
# print(text.index("cat"))       # ValueError!

# count: 统计出现次数
print(text.count("the"))         # 2

# replace: 替换（返回新字符串）
new_text = text.replace("fox", "cat")
print(new_text)                  # the quick brown cat jumps...

# startswith / endswith
print(text.startswith("the"))    # True
print(text.endswith("dog"))      # True

# strip: 去除首尾空白或指定字符
data = "   hello  world   \n"
print(data.strip())              # "hello  world"
print("###title###".strip("#"))  # "title"
```

**案例3：工业级——模板字符串的安全渲染**

```python
import re
import string
from typing import Dict, Any

class SafeTemplate:
    """
    安全的字符串模板引擎（简化版）。
    支持 ${variable} 语法，对未定义的变量报错而非静默忽略。
    相比 str.format() 更安全，不会执行任意表达式。
    """

    _PATTERN = re.compile(r'\$\{(\w+)\}')

    @classmethod
    def render(cls, template: str, context: Dict[str, Any]) -> str:
        """
        渲染模板，严格检查所有变量是否已定义。

        例子:
            tpl = "Hello, ${name}! Your score is ${score}."
            ctx = {"name": "Alice", "score": 95}
            result = SafeTemplate.render(tpl, ctx)
            # "Hello, Alice! Your score is 95."
        """
        def replacer(match):
            var_name = match.group(1)
            if var_name not in context:
                raise KeyError(f"模板变量未定义: '{var_name}'")
            return str(context[var_name])

        return cls._PATTERN.sub(replacer, template)

    @classmethod
    def extract_variables(cls, template: str) -> set:
        """提取模板中的所有变量名，用于校验"""
        return set(cls._PATTERN.findall(template))


# 使用演示
sql_template = "SELECT ${columns} FROM ${table} WHERE id = ${user_id}"
vars_needed = SafeTemplate.extract_variables(sql_template)
print(f"需要的变量: {vars_needed}")  # {'columns', 'table', 'user_id'}

context = {"columns": "name, age", "table": "users", "user_id": 42}
result = SafeTemplate.render(sql_template, context)
print(result)  # SELECT name, age FROM users WHERE id = 42
```

---

### 知识点：字符串格式化——% / format / f-string

**案例1：三种格式化方式的对比**

```python
name = "Alice"
age = 30
score = 95.5678

# 方式1：% 格式化（旧式，不推荐）
s1 = "姓名: %s, 年龄: %d, 分数: %.2f" % (name, age, score)
print(s1)

# 方式2：str.format()（新式，兼容性好）
s2 = "姓名: {}, 年龄: {}, 分数: {:.2f}".format(name, age, score)
s3 = "姓名: {n}, 年龄: {a}, 分数: {s:.2f}".format(n=name, a=age, s=score)
print(s2)
print(s3)

# 方式3：f-string（Python 3.6+，最推荐）
s4 = f"姓名: {name}, 年龄: {age}, 分数: {score:.2f}"
print(s4)

# f-string 支持任意表达式
print(f"明年年龄: {age + 1}")
print(f"名字大写: {name.upper()}")
```

**案例2：格式规范微语言**

```python
# 数字格式化
n = 1234567.89

print(f"{n:.2f}")        # 1234567.89   — 保留2位小数
print(f"{n:,.2f}")       # 1,234,567.89 — 千位分隔符
print(f"{n:>15,.2f}")    #   1,234,567.89 — 右对齐，宽度15
print(f"{n:0>15,.2f}")   # 001,234,567.89 — 右对齐，0填充
print(f"{n:.2e}")        # 1.23e+06     — 科学计数法
print(f"{0.865:.2%}")    # 86.50%       — 百分比

# 字符串格式化
name = "Bob"
print(f"|{name:<10}|")   # |Bob       | — 左对齐，宽度10
print(f"|{name:>10}|")   # |       Bob| — 右对齐
print(f"|{name:^10}|")   # |   Bob    | — 居中对齐
print(f"|{name:*^10}|")  # |***Bob****| — *填充居中

# 日期格式化
from datetime import datetime
now = datetime(2026, 7, 14, 15, 30, 0)
print(f"{now:%Y-%m-%d %H:%M:%S}")   # 2026-07-14 15:30:00
```

**案例3：工业级——日志格式化器（含彩色输出）**

```python
import logging
import time
from datetime import datetime
from typing import Optional

class ColoredFormatter(logging.Formatter):
    """
    带颜色的日志格式化器。
    不同级别用不同颜色，方便开发和运维排查问题。
    """

    # ANSI 颜色码
    COLORS = {
        "DEBUG": "\033[36m",     # 青色
        "INFO": "\033[32m",      # 绿色
        "WARNING": "\033[33m",   # 黄色
        "ERROR": "\033[31m",     # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True):
        fmt = (
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
        )
        super().__init__(fmt, datefmt="%Y-%m-%d %H:%M:%S")
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        if self.use_colors:
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


# 使用演示
logger = logging.getLogger("MyApp")
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(use_colors=True))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.debug("数据库连接池参数: host=127.0.0.1, pool_size=10")
logger.info("服务启动完成，端口 8080")
logger.warning("CPU 使用率超过 80%")
logger.error("无法连接 Redis: Connection refused")
logger.critical("磁盘空间不足，服务即将停止")
```

---

## 2.3 运算符

### 知识点：逻辑运算符与短路求值

**案例1：短路求值的基本演示**

```python
# and: 左边为 False 时，右边不执行
def expensive_check():
    print("执行了昂贵的检查！")
    return True

result = False and expensive_check()
# 没有任何输出 — expensive_check() 没有被调用
print(f"result = {result}")  # False

# or: 左边为 True 时，右边不执行
result = True or expensive_check()
# 没有任何输出 — expensive_check() 没有被调用
print(f"result = {result}")  # True
```

**案例2：利用短路求值实现默认值**

```python
# 常见模式：如果第一个值是 Falsy，用第二个
def get_config_value(key, default):
    # config[key] 可能返回 None 或 0，需要明确处理
    value = get_from_redis(key)  # 可能返回 None
    return value if value is not None else default

# 更 Pythonic 的写法
def get_config_value(key, default):
    value = get_from_redis(key)
    return value or default  # 注意！如果 value=0 或空字符串也会触发 default

# 最安全的方式（Python 3.8+）：海象运算符
def get_config_value(key, default):
    if (value := get_from_redis(key)) is not None:
        return value
    return default
```

**案例3：工业级——权限校验链（短路求值实践）**

```python
from functools import wraps
from typing import Callable, List, Optional

class Permission:
    """权限系统：多个检查器用短路求值串联"""

    def __init__(self, name: str):
        self.name = name
        self._checkers: List[Callable[[dict], bool]] = []

    def add_checker(self, checker: Callable[[dict], bool]) -> "Permission":
        self._checkers.append(checker)
        return self

    def check(self, user: dict) -> bool:
        """
        执行所有检查器，遇到第一个失败的立即返回 False。
        这就是短路求值在业务逻辑中的应用。
        """
        for checker in self._checkers:
            if not checker(user):
                return False
        return True


# 定义各种检查器
def is_authenticated(user: dict) -> bool:
    return user.get("authenticated", False)

def is_active(user: dict) -> bool:
    return user.get("is_active", False)

def has_role(role: str) -> Callable[[dict], bool]:
    def checker(user: dict) -> bool:
        return role in user.get("roles", [])
    return checker

def is_not_expired(user: dict) -> bool:
    from datetime import datetime
    expiry = user.get("expiry_date")
    if not expiry:
        return True
    return expiry > datetime.now()


# 组合权限
admin_permission = (
    Permission("管理员权限")
    .add_checker(is_authenticated)          # 1. 先检查是否登录
    .add_checker(is_active)                 # 2. 检查账号是否激活
    .add_checker(has_role("admin"))         # 3. 检查是否有 admin 角色
    .add_checker(is_not_expired)            # 4. 检查是否过期
)

# 测试
user = {"authenticated": True, "is_active": True, "roles": ["admin"]}
print(f"admin权限通过: {admin_permission.check(user)}")  # True

user2 = {"authenticated": True, "is_active": False, "roles": ["admin"]}
print(f"admin权限通过: {admin_permission.check(user2)}")  # False（is_active 检查就拦截了，后面的不执行）
```

---

### 知识点：海象运算符 `:=`（Python 3.8+）

**案例1：if 语句中的海象运算符**

```python
# ❌ 传统写法：函数调用了两次
import re

text = "User ID: 12345"
match = re.search(r"\d+", text)
if match:
    print(f"找到数字: {match.group()}")   # 找到数字: 12345

# ✅ 海象运算符：赋值和判断一步完成
if (match := re.search(r"\d+", text)):
    print(f"找到数字: {match.group()}")   # 找到数字: 12345
```

**案例2：while 循环中逐块读取数据**

```python
# ❌ 传统写法
chunk = read_chunk()
while chunk:
    process(chunk)
    chunk = read_chunk()

# ✅ 海象运算符
while (chunk := read_chunk()):
    process(chunk)

# 实际例子：逐行读取文件
with open("large_file.txt") as f:
    while (line := f.readline().strip()):
        print(f"处理行: {line}")
```

**案例3：工业级——流式数据处理的管道模式**

```python
from typing import Iterator, List, Callable, Optional
import re

class LogPipeline:
    """
    日志处理管道。用海象运算符逐行消费流式数据，
    避免一次性加载整个文件到内存。
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._filters: List[Callable[[str], bool]] = []
        self._transformers: List[Callable[[str], str]] = []

    def add_filter(self, pred: Callable[[str], bool]) -> "LogPipeline":
        self._filters.append(pred)
        return self

    def add_transformer(self, transform: Callable[[str], str]) -> "LogPipeline":
        self._transformers.append(transform)
        return self

    def process(self) -> Iterator[str]:
        """流式处理，逐行过滤和转换"""
        with open(self.filepath) as f:
            while (line := f.readline().strip()):
                # 过滤
                if not all(f(line) for f in self._filters):
                    continue
                # 转换
                for t in self._transformers:
                    line = t(line)
                yield line

    def count_errors(self) -> int:
        """统计错误数量（利用海象运算符的短路模式）"""
        count = 0
        pipe = self.process()
        while (line := next(pipe, None)) is not None:
            if "ERROR" in line:
                count += 1
        return count


# 使用演示
# 假设有一个 app.log 文件
# pipeline = (
#     LogPipeline("app.log")
#     .add_filter(lambda line: bool(line))
#     .add_transformer(lambda line: line.upper())
# )
# for processed in pipeline.process():
#     print(processed)
```

---

## 本章速查

| 类型 | 可变性 | 典型操作 |
|------|--------|----------|
| `int` | 不可变 | 任意精度，不会溢出 |
| `float` | 不可变 | IEEE 754，有精度问题，用 `math.isclose` 比较 |
| `bool` | 不可变 | True/False，是 int 的子类 |
| `str` | 不可变 | 切片、split/join、三种格式化方式 |
| `None` | 单例 | 表示"没有值"，用 `is` 判断 |

| 运算符 | 说明 |
|--------|------|
| `and` `or` `not` | 逻辑运算符，短路求值 |
| `:=` | 海象运算符，表达式内赋值 |
| `is` | 判断身份（是否同一个对象） |
| `==` | 判断值是否相等 |
