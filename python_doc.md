# Python 基础知识体系大纲

> 循序渐进，逐点吃透。已掌握的打 ✅，学习中打 🔄，疑难的打 ❓。

---

## 第一章：环境搭建与工具链

### 1.1 Python 解释器
- [ ] CPython vs PyPy vs Jython 区别
- [ ] Python 2.x 与 3.x 的核心差异
- [ ] 解释器的工作原理：编译成字节码 → PVM 执行
- [ ] `python -m` 的用法和原理

### 1.2 环境管理
- [ ] pip 包管理（install / uninstall / freeze / list）
- [ ] 虚拟环境：venv 的创建、激活、退出
- [ ] pipenv / poetry / conda 的基本概念
- [ ] requirements.txt 的生成和安装

### 1.3 开发工具
- [ ] IDE 选择（PyCharm / VS Code / Jupyter）
- [ ] 调试器（pdb / IDE 断点调试）
- [ ] 代码格式化（black / ruff）
- [ ] 类型检查（mypy）

---

## 第二章：基础语法

### 2.1 变量与基本数据类型
- [ ] 变量的本质：名字 → 对象的引用（不是盒子）
- [ ] `id()` 和 `is` 判断对象身份
- [ ] int（任意精度整数）
- [ ] float（IEEE 754 双精度，精度问题）
- [ ] bool（True/False，是 int 的子类）
- [ ] complex（复数）
- [ ] None（NoneType，单例）

### 2.2 字符串 (str)
- [ ] 引号：单引号、双引号、三引号
- [ ] 转义字符 `\n` `\t` `\\` 与原始字符串 `r""`
- [ ] 字符串不可变性
- [ ] 索引与切片 `s[0]` `s[1:5]` `s[::-1]`
- [ ] 拼接与重复 `+` `*` `join()`
- [ ] 常用方法：`split()` `strip()` `replace()` `find()` `count()` `startswith()` `endswith()`
- [ ] 大小写转换：`upper()` `lower()` `title()` `capitalize()` `swapcase()`
- [ ] 判断类方法：`isdigit()` `isalpha()` `isalnum()` `isspace()`
- [ ] 格式化输出：
  - `%` 格式化（旧式）
  - `str.format()`（新式）
  - f-string `f"{var}"`（Python 3.6+，推荐）
  - 格式规范微语言：`:.2f` `:>10` `:,` `:.2%`

### 2.3 运算符
- [ ] 算术运算符：`+` `-` `*` `/` `//` `%` `**`
- [ ] 比较运算符：`==` `!=` `>` `<` `>=` `<=` `is` `in`
- [ ] 逻辑运算符：`and` `or` `not`（短路求值）
- [ ] 位运算符：`&` `|` `^` `~` `<<` `>>`
- [ ] 赋值运算符：`=` `+=` `-=` 等
- [ ] 运算符优先级总览
- [ ] 海象运算符 `:=`（Python 3.8+）

### 2.4 类型转换
- [ ] 显式转换：`int()` `float()` `str()` `bool()` `list()` `tuple()` `set()`
- [ ] 隐式转换（布尔上下文、数值运算）

---

## 第三章：程序流程控制

### 3.1 条件判断
- [ ] `if / elif / else` 语法
- [ ] 三元表达式 `x if cond else y`
- [ ] 真值测试：哪些值判定为 False（None, 0, 0.0, "", [], {}, set(), 自定义 `__bool__`）
- [ ] `match / case` 模式匹配（Python 3.10+）

### 3.2 循环
- [ ] `while` 循环
- [ ] `while True` + break 模式
- [ ] `while / else`（正常退出才执行 else）
- [ ] `for` 循环的本质（迭代器协议）
- [ ] `for / else`
- [ ] `break`（终止整个循环）
- [ ] `continue`（跳过本次迭代）
- [ ] `pass` 占位语句

### 3.3 可迭代对象与迭代器（核心概念）
- [ ] 可迭代对象 vs 迭代器的区别
- [ ] 迭代器协议：`__iter__()` + `__next__()`
- [ ] `iter()` 和 `next()` 内置函数
- [ ] `StopIteration` 异常
- [ ] 自定义迭代器类
- [ ] `collections.abc.Iterable` 和 `Iterator`

---

## 第四章：内置容器类型 —— 四种核心数据结构

### 4.1 列表 (list)
- [ ] 创建方式：`[]` `list()` 列表推导式
- [ ] 增：`append()` `insert()` `extend()` `+`
- [ ] 删：`remove()` `pop()` `del` `clear()`
- [ ] 改：索引赋值、切片赋值
- [ ] 查：`index()` `count()` `in`
- [ ] 排序：`sort()` vs `sorted()`，`reverse` 参数，`key` 函数
- [ ] 反转：`reverse()` vs `reversed()` vs `[::-1]`
- [ ] 复制：浅拷贝 vs 深拷贝（`copy()` `[:]` `copy.deepcopy()`）
- [ ] 列表推导式（详见第七章）
- [ ] 多维列表与矩阵操作

### 4.2 元组 (tuple)
- [ ] 不可变序列的本质
- [ ] 创建方式：`()` `tuple()` 逗号
- [ ] 单元素元组：`(1,)` ← 逗号是关键
- [ ] 封包（packing）与解包（unpacking）
- [ ] 星号解包：`a, *b, c = (1,2,3,4,5)`
- [ ] 命名元组 `collections.namedtuple`
- [ ] 元组为什么比列表快？何时用元组？

### 4.3 字典 (dict) —— 最核心
- [ ] 哈希表原理（通俗理解）
- [ ] 键的要求：可哈希（不可变）
- [ ] 创建：`{}` `dict()` 字典推导式 `dict.fromkeys()`
- [ ] 增/改：`d[key]=val` `update()` `setdefault()`
- [ ] 删：`pop()` `popitem()` `del` `clear()`
- [ ] 查：`d[key]` `get()`（安全取值）
- [ ] 遍历：`.keys()` `.values()` `.items()`
- [ ] 成员判断：`key in d`（O(1) 时间复杂度）
- [ ] 字典合并：`|` 运算符（Python 3.9+）`{**d1, **d2}`（解包合并）
- [ ] 默认字典 `collections.defaultdict`
- [ ] 有序字典 `collections.OrderedDict`
- [ ] 计数器 `collections.Counter`

### 4.4 集合 (set)
- [ ] 底层也是哈希表（值就是键）
- [ ] 可变集合 `set()` vs 不可变集合 `frozenset()`
- [ ] 创建：`set()` `{1,2,3}` 集合推导式（不能是空的 `{}`——那是字典）
- [ ] 增删：`add()` `remove()` `discard()` `pop()`
- [ ] 集合运算：`|` `&` `-` `^`（并、交、差、对称差）
- [ ] 子集/超集判断：`<=` `>=` `<` `>`
- [ ] 去重的标准做法
- [ ] 集合推导式

---

## 第五章：函数 —— 抽象的第一层

### 5.1 函数基础
- [ ] 定义：`def` 关键字
- [ ] 参数 vs 实参（形参 vs 实参）的概念
- [ ] `return` 返回值（无 return 返回 None）
- [ ] 多返回值（本质是返回一个元组）
- [ ] `None` 作为默认返回值
- [ ] 文档字符串 `"""..."""` 和 `help()`

### 5.2 参数传递（核心难点）
- [ ] Python 的参数传递是"传对象引用"（call by sharing）
- [ ] 可变对象 vs 不可变对象作为参数的差异
- [ ] 位置参数（positional arguments）
- [ ] 关键字参数（keyword arguments）
- [ ] 默认参数（默认值的陷阱：只在定义时求值一次！）
- [ ] 可变参数 `*args`（打包成元组）
- [ ] 关键字可变参数 `**kwargs`（打包成字典）
- [ ] 解包调用：`func(*list)` `func(**dict)`
- [ ] 参数顺序规则：位置 → `*args` → 关键字 → `**kwargs`
- [ ] keyword-only 参数（`*` 之后或 `*args` 之后的参数）
- [ ] positional-only 参数（`/` 之前，Python 3.8+）
- [ ] 参数组合的完整语法：`def f(pos, /, pos_or_kw, *, kw_only)`

### 5.3 作用域与命名空间
- [ ] LEGB 规则详解（Local → Enclosing → Global → Built-in）
- [ ] `global` 关键字
- [ ] `nonlocal` 关键字
- [ ] `globals()` `locals()` 内置函数
- [ ] 闭包（Closure）的本质和形成条件
- [ ] `__code__` `__closure__` 属性窥探闭包内部

### 5.4 匿名函数 lambda
- [ ] `lambda 参数: 表达式`（只有一行表达式）
- [ ] lambda 的限制（不能有语句、不能有类型注解）
- [ ] 与 `map()` `filter()` `sorted(key=...)` 配合
- [ ] 为什么不推荐 lambda 赋值给变量？（用 def）
- [ ] lambda 与闭包的陷阱

### 5.5 内置高阶函数
- [ ] `map(func, iterable)` — 每一个元素映射
- [ ] `filter(func, iterable)` — 筛选
- [ ] `reduce(func, iterable)` — 累积归约（functools）
- [ ] `sorted(iterable, key=func, reverse=...)`
- [ ] `any()` / `all()` — 存在量词 / 全称量词
- [ ] `enumerate()` — 带索引遍历
- [ ] `zip()` — 并行迭代
- [ ] 推导式 vs map/filter（推导式更 Pythonic）

### 5.6 装饰器（Decorator）
- [ ] 函数是一等对象（可赋值给变量、可作为参数、可作为返回值）
- [ ] 装饰器本质：接受函数，返回新函数
- [ ] 最简单的装饰器写法
- [ ] `@decorator` 语法糖原理
- [ ] 带参数的装饰器（三层嵌套）
- [ ] 保留元数据 `functools.wraps`
- [ ] 多个装饰器的执行顺序（由内到外）
- [ ] 类装饰器 `__call__` 方法
- [ ] 实战：计时器、日志、权限校验、缓存、重试

### 5.7 递归
- [ ] 递归三要素：终止条件、缩小规模、调用自身
- [ ] 经典例题：阶乘、斐波那契、汉诺塔
- [ ] 递归的调用栈可视化
- [ ] 递归深度限制 `sys.setrecursionlimit()`
- [ ] 尾递归优化（Python 不支持，为什么？）
- [ ] 用栈模拟递归（迭代改写）

---

## 第六章：生成器与迭代器（深入）

### 6.1 生成器函数
- [ ] `yield` 关键字的工作原理
- [ ] 生成器函数的调用：返回生成器对象，不执行函数体
- [ ] `yield` vs `return` 的底层差异
- [ ] 生成器的执行模型：暂停 → 恢复
- [ ] `StopIteration` 自动抛出
- [ ] 生成器的状态（GEN_CREATED / GEN_RUNNING / GEN_SUSPENDED / GEN_CLOSED）

### 6.2 生成器的高级特性
- [ ] `send()` — 向生成器注入数据
- [ ] `throw()` — 向生成器抛入异常
- [ ] `close()` — 关闭生成器（触发 GeneratorExit）
- [ ] `yield from` — 委托子生成器
- [ ] `yield from` 的透明双向通道

### 6.3 生成器表达式
- [ ] `(x for x in iterable if cond)`
- [ ] 和列表推导式的区别：惰性 vs 立即
- [ ] 作为函数唯一参数时省略括号
- [ ] 性能对比：内存开销

### 6.4 实战应用
- [ ] 大文件逐行处理
- [ ] 无限序列
- [ ] 数据管道（Pipeline）
- [ ] 流式处理模式

---

## 第七章：推导式 —— Python 最优雅的语法

### 7.1 列表推导式
- [ ] 基础语法：`[表达式 for x in iterable]`
- [ ] 带过滤：`[... if cond]`（if 在 for 后）
- [ ] 带变换：`[a if cond else b for ...]`（if-else 在 for 前）
- [ ] 嵌套循环：`[... for x in A for y in B]`
- [ ] 多条件过滤
- [ ] 推导式 vs 传统 for 循环的性能差异

### 7.2 字典推导式
- [ ] `{k: v for k, v in iterable}`
- [ ] 键值互换
- [ ] 带过滤的字典构建

### 7.3 集合推导式
- [ ] `{x for x in iterable if cond}`
- [ ] 去重场景

### 7.4 生成器表达式（惰性推导式）
- [ ] `(x for x in iterable)`
- [ ] 大数据量场景的选择
- [ ] 搭配 `sum()` `any()` `all()` `max()` `min()` `join()`

---

## 第八章：异常处理

### 8.1 异常基础
- [ ] `try / except / else / finally` 四件套
- [ ] 捕获多个异常：`except (A, B) as e`
- [ ] 获取异常信息：`as e`
- [ ] else 的执行条件（try 块无异常才执行）
- [ ] finally 的执行保证（即使 return 也会执行）
- [ ] 异常层级结构（BaseException → Exception → 各种子类）

### 8.2 常见内置异常
- [ ] `SyntaxError` / `IndentationError`
- [ ] `NameError` / `UnboundLocalError`
- [ ] `TypeError` / `ValueError`
- [ ] `IndexError` / `KeyError`
- [ ] `AttributeError`
- [ ] `FileNotFoundError` / `IOError` / `OSError`
- [ ] `ZeroDivisionError`
- [ ] `ImportError` / `ModuleNotFoundError`
- [ ] `KeyboardInterrupt`

### 8.3 自定义异常
- [ ] 继承 Exception 类
- [ ] `raise` 抛出异常
- [ ] `raise from` 异常链
- [ ] `__cause__` 和 `__context__` 属性
- [ ] 异常的最佳实践

### 8.4 上下文管理器
- [ ] `with` 语句的底层原理
- [ ] `__enter__` 和 `__exit__` 方法
- [ ] `contextlib.contextmanager` 装饰器（用生成器写上下文管理器）
- [ ] 实战：文件操作、数据库连接、锁管理

---

## 第九章：文件操作

### 9.1 文件读写基础
- [ ] 打开模式：`r` `w` `a` `x` `b` `t` `+`
- [ ] 文本模式 vs 二进制模式
- [ ] 编码：`utf-8` `gbk` 等，乱码问题的根源
- [ ] `open()` → `read()` `readline()` `readlines()`
- [ ] `write()` `writelines()`
- [ ] `with open(...) as f` 自动关闭（为什么必须用 with）

### 9.2 文件操作进阶
- [ ] `seek()` `tell()` 文件指针操作
- [ ] `os` 模块：`os.path` 路径操作
- [ ] `pathlib.Path`（现代写法，推荐）
- [ ] 遍历目录 `os.walk()` `Path.rglob()`
- [ ] CSV 文件：`csv` 模块
- [ ] JSON 文件：`json.dumps()` `json.loads()` `json.dump()` `json.load()`
- [ ] pickle 序列化（及其安全问题）

---

## 第十章：面向对象编程 (OOP)

### 10.1 类与对象基础
- [ ] `class` 关键字定义类
- [ ] `__init__` 构造方法
- [ ] `self` 是什么，为什么必须有（绑定方法）
- [ ] 实例属性 vs 类属性
- [ ] 实例方法 vs 类方法（`@classmethod`）vs 静态方法（`@staticmethod`）
- [ ] 方法的第一个参数：`self` vs `cls`

### 10.2 访问控制
- [ ] Python 没有真正的私有（靠约定和 name mangling）
- [ ] `_name`：约定为"受保护的"
- [ ] `__name`：名称改写（name mangling）→ `_ClassName__name`
- [ ] `@property` 装饰器（getter / setter / deleter）
- [ ] 属性的底层：描述符协议（`__get__` `__set__` `__delete__`）

### 10.3 魔术方法（Dunder Methods）
- [ ] `__str__` vs `__repr__` 的区别和使用场景
- [ ] `__len__` `__bool__`（len() 和 bool() 行为）
- [ ] `__getitem__` `__setitem__` `__delitem__`（模拟容器）
- [ ] `__iter__` `__next__`（可迭代对象和迭代器）
- [ ] `__contains__`（in 操作符）
- [ ] `__call__`（让实例像函数一样调用）
- [ ] `__enter__` `__exit__`（上下文管理器）
- [ ] `__eq__` `__lt__` `__gt__` 等（比较运算符）
- [ ] `__add__` `__sub__` `__mul__` 等（算术运算符）
- [ ] `__hash__`（配合 `__eq__`，对象可哈希）
- [ ] `__new__` vs `__init__`（创建 vs 初始化）
- [ ] `__slots__`（节省内存、禁止动态属性）

### 10.4 继承
- [ ] 单继承：`class Child(Parent)`
- [ ] `super()` 的用法和 MRO（方法解析顺序）
- [ ] `__mro__` 属性和 C3 线性化算法（通俗理解）
- [ ] 多继承和钻石继承问题
- [ ] `isinstance()` vs `issubclass()`
- [ ] Mixin 模式（多继承的推荐用法）
- [ ] 抽象基类 `abc.ABC` / `@abstractmethod`

### 10.5 高级 OOP 概念
- [ ] 鸭子类型（Duck Typing）—— Python 的核心哲学
- [ ] 协议（Protocol）：静态鸭子类型（`typing.Protocol`）
- [ ] 数据类 `@dataclass`（Python 3.7+）
- [ ] 枚举 `enum.Enum`
- [ ] `__init_subclass__` 钩子

---

## 第十一章：模块与包

### 11.1 模块
- [ ] `import module` vs `from module import name`
- [ ] `import module as alias` 别名
- [ ] 模块搜索路径 `sys.path`
- [ ] `__name__` 和 `"__main__"`（程序入口判断）
- [ ] `dir()` 查看模块内容
- [ ] 模块只会被导入一次（缓存 `sys.modules`）
- [ ] 相对导入 vs 绝对导入

### 11.2 包
- [ ] 包即目录，`__init__.py`（Python 3.3+ 可省略）
- [ ] `__init__.py` 的作用
- [ ] `__all__` 列表控制 `from xx import *`
- [ ] 命名空间包（PEP 420）
- [ ] 循环导入问题及解决方案

### 11.3 常用标准库速览
- [ ] `os` / `os.path` — 操作系统接口
- [ ] `sys` — 系统相关参数（`argv` `path` `stdin/stdout/stderr`）
- [ ] `math` / `random` — 数学运算
- [ ] `datetime` / `time` / `calendar` — 日期和时间
- [ ] `collections` — 高级容器（deque, Counter, defaultdict, OrderedDict, ChainMap）
- [ ] `itertools` — 迭代器工具（count, cycle, repeat, chain, combinations, permutations, product）
- [ ] `functools` — 高阶函数工具（reduce, partial, lru_cache, wraps, singledispatch）
- [ ] `re` — 正则表达式
- [ ] `argparse` — 命令行参数解析
- [ ] `logging` — 日志系统
- [ ] `subprocess` — 子进程管理
- [ ] `threading` / `multiprocessing` — 并发
- [ ] `asyncio` — 异步 I/O
- [ ] `unittest` / `pytest` — 单元测试
- [ ] `typing` — 类型注解

---

## 第十二章：内存管理与底层机制

### 12.1 对象与引用
- [ ] 一切都是对象（int、函数、类本身都是对象）
- [ ] 引用计数 + 循环检测垃圾回收（gc 模块）
- [ ] `sys.getrefcount()` 查看引用计数
- [ ] 小整数缓存池（-5 ~ 256）
- [ ] 字符串驻留（interning）机制
- [ ] `is` vs `==` 的底层差异

### 12.2 可变与不可变
- [ ] 不可变：int, float, str, tuple, frozenset, bytes
- [ ] 可变：list, dict, set, bytearray
- [ ] 为什么重要？（传参行为、哈希、线程安全）
- [ ] `+=` 对可变/不可变对象的差异

### 12.3 深浅拷贝
- [ ] 赋值 `=` 不复制，只是多一个引用
- [ ] 浅拷贝：`copy.copy()` `list[:]` `d.copy()`
- [ ] 深拷贝：`copy.deepcopy()`
- [ ] 可视化理解

---

## 第十三章：并发与异步

### 13.1 并发基础概念
- [ ] 并发的本质
- [ ] 进程 vs 线程 vs 协程
- [ ] 并行 vs 并发
- [ ] CPU 密集型 vs I/O 密集型

### 13.2 GIL（全局解释器锁）
- [ ] GIL 是什么，为什么存在
- [ ] GIL 对多线程的影响
- [ ] 绕过 GIL 的方案

### 13.3 多线程 (threading)
- [ ] `threading.Thread` 创建和启动
- [ ] `join()` 等待线程结束
- [ ] `Lock` 互斥锁
- [ ] `RLock` 可重入锁
- [ ] `Queue` 线程安全队列
- [ ] 线程池 `concurrent.futures.ThreadPoolExecutor`

### 13.4 多进程 (multiprocessing)
- [ ] `multiprocessing.Process`
- [ ] `Pool` / `PoolExecutor`
- [ ] 进程间通信（Queue, Pipe）
- [ ] 共享内存

### 13.5 异步编程 (asyncio) [可选进阶]
- [ ] 协程：`async def` / `await`
- [ ] 事件循环（Event Loop）概念
- [ ] `asyncio.run()` `asyncio.gather()` `asyncio.create_task()`
- [ ] 异步上下文管理器 `async with`
- [ ] 异步迭代器 `async for`

---

## 第十四章：类型注解与静态检查

### 14.1 类型注解基础
- [ ] 变量注解：`x: int = 5`
- [ ] 函数注解：`def f(x: int) -> str`
- [ ] 基本类型：`int` `float` `str` `bool` `None`
- [ ] 容器类型：`list[int]` `dict[str, int]` `tuple[int, str]` `set[float]`
- [ ] 可选类型：`Optional[str]` = `str | None`
- [ ] 联合类型：`Union[int, str]` = `int | str`（Python 3.10+）
- [ ] `Any` — 任意类型
- [ ] `Callable[[int, str], bool]` — 可调用对象

### 14.2 高级类型
- [ ] `Literal["a", "b"]` — 字面量类型
- [ ] `TypedDict` — 类型化字典
- [ ] `Protocol` — 结构化子类型
- [ ] `TypeVar` — 泛型变量
- [ ] `Generic` — 泛型类

### 14.3 工具链
- [ ] mypy 静态检查
- [ ] `typing.TYPE_CHECKING` 避免循环导入
- [ ] 运行时获取类型 `typing.get_type_hints()`
- [ ] `@dataclass` 与类型注解

---

## 第十五章：测试

### 15.1 单元测试
- [ ] `unittest` 框架
- [ ] `TestCase` 子类，`setUp` / `tearDown`
- [ ] 断言方法：`assertEqual` `assertTrue` `assertRaises` 等
- [ ] `pytest`（第三方，实际标准）
- [ ] `pytest` fixture 机制
- [ ] 参数化测试 `@pytest.mark.parametrize`
- [ ] mock / patch 隔离依赖

### 15.2 其他测试
- [ ] doctest（文档即测试）
- [ ] 覆盖率 `coverage`
- [ ] TDD（测试驱动开发）的基本流程

---

## 第十六章：实战项目路线图

### 入门级
- [ ] 命令行计算器
- [ ] 猜数字游戏
- [ ] 待办事项清单（命令行版）
- [ ] 密码生成器
- [ ] 文本统计器（词频、行数）

### 进阶级
- [ ] Web 爬虫（requests + BeautifulSoup）
- [ ] REST API 客户端
- [ ] 文件批量重命名工具
- [ ] Markdown 转 HTML 工具
- [ ] 简单的博客系统（Flask / FastAPI）

### 高级
- [ ] 自动化运维脚本
- [ ] 数据分析与可视化（pandas + matplotlib）
- [ ] 简单的 ORM 实现
- [ ] WebSocket 聊天室
- [ ] 个人知识库 / 笔记系统

---

## 附录：学习资源推荐

| 类别 | 资源 |
|------|------|
| **官方文档** | [docs.python.org/zh-cn/3](https://docs.python.org/zh-cn/3/) |
| **必读书** | 《流畅的 Python》（进阶）、《Python 编程：从入门到实践》 |
| **在线练习** | LeetCode（算法）、CheckiO（游戏化） |
| **风格指南** | PEP 8（代码风格）、PEP 257（文档字符串） |
| **进阶读物** | Python Cookbook、《Python 源码剖析》 |

---

> **使用方式**：
> 1. 每天选定一个未标记 ✅ 的小节
> 2. 动手写代码验证每一个知识点
> 3. 用自己的话做笔记（费曼学习法）
> 4. 标记掌握状态：✅ 掌握 | 🔄 学习中 | ❓ 有疑问
> 5. 每周回顾打 ✅ 的内容，确保没有遗忘
