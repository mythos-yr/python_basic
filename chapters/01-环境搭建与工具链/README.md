# 第一章：环境搭建与工具链

---

## 1.1 Python 解释器

### 理论：Python 程序是怎么跑起来的？

你写的 `.py` 文件，计算机怎么"读懂"并执行？分三步：

```
你写的源代码(.py) → 编译成字节码(.pyc) → Python虚拟机逐条执行
   (人类可读)        (中间表示)            (真正干活)
```

**类比**：你写了一本菜谱（源代码），翻译成厨师能懂的标准化指令（字节码），厨师照着做菜（虚拟机执行）。

**CPython** 是官方解释器，用 C 语言写的。此外还有 PyPy（带 JIT 加速器，跑得快）和 Jython（跑在 Java 平台上）。

Python 是**语言规范**，CPython/PyPy/Jython 是这个规范的**不同实现**——就像"汽车"是概念，特斯拉和丰田是不同的实现。

---

### 关键字/命令

| 命令 | 作用 |
|------|------|
| `python` | 启动交互式解释器 |
| `python file.py` | 执行脚本 |
| `python -c "code"` | 执行一行代码 |
| `python -m module` | 把模块当做脚本运行 |

`-m` 的意思是：Python 自动在 `sys.path` 中搜索该模块并执行。

---

### 案例

**案例1：查看当前解释器信息**

```python
import sys, platform

print(f"版本: {sys.version_info.major}.{sys.version_info.minor}")
print(f"实现: {platform.python_implementation()}")  # CPython / PyPy
print(f"路径: {sys.executable}")
```

**案例2：查看 Python 代码编译后的底层字节码**

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
# LOAD_FAST  (a)     ← 把 a 加载到栈上
# LOAD_FAST  (b)     ← 把 b 加载到栈上
# BINARY_OP  (+)     ← 弹出两个值，做加法
# RETURN_VALUE       ← 返回结果
```

**案例3：用 compile/exec 理解"编译和执行是分开的"**

```python
source = "x = 10\ny = 20\nresult = x + y"
code = compile(source, "<demo>", "exec")  # 编译
ns = {}
exec(code, ns)                              # 执行
print(ns["result"])  # 30
```

---

## 1.2 虚拟环境 (venv)

### 理论：为什么需要虚拟环境？

项目A 需要 `requests==2.20`，项目B 需要 `requests==2.28`。全局只能装一个版本，冲突了。

**虚拟环境 = 给每个项目一个独立的"包安装空间"**，互不干扰。

类比：
- 全局环境 = 公共图书馆（谁都在里面放书，容易乱）
- 虚拟环境 = 每个项目自带独立小书架

虚拟环境**不是完整复制 Python**，只是创建一个隔离目录，里面有独立的 `site-packages`。

---

### 关键字/命令

```bash
python -m venv .venv             # 创建
source .venv/bin/activate        # 激活 (macOS/Linux)
.venv\Scripts\activate           # 激活 (Windows)
deactivate                       # 退出
```

检测是否在虚拟环境中：

```python
import sys
print(sys.prefix != sys.base_prefix)  # True = 在虚拟环境中
```

---

### 案例

**案例1：完整流程**

```bash
python -m venv .venv
source .venv/bin/activate
which python                   # 应指向 .venv/bin/python
pip install requests pandas
pip freeze > requirements.txt
deactivate
```

**案例2：在新环境一键复现依赖**

```bash
pip install -r requirements.txt
```

**案例3：pip 常用命令**

```bash
pip install pkg==1.2.3      # 装指定版本
pip install "pkg>=2.0,<3.0" # 版本范围
pip list --outdated         # 哪些包有新版本
pip show pkg                # 包详细信息
pip check                   # 依赖冲突检查
```

---

## 1.3 调试器 (pdb)

### 理论：调试器是"时间暂停器"

程序跑得飞快，出 bug 时你来不及看清楚发生了什么。pdb 让程序在任意一行**暂停**，你可以检查所有变量的值，然后一行一行地执行。

---

### 关键字/命令

```python
breakpoint()  # Python 3.7+ 推荐的断点（程序在此暂停）
```

进入 pdb 后最常用的 5 个命令：

| 命令 | 全称 | 作用 |
|------|------|------|
| `n` | next | 执行下一行 |
| `s` | step | 步入函数内部 |
| `c` | continue | 继续执行到下一个断点 |
| `p 变量` | print | 打印变量值 |
| `q` | quit | 退出 |

---

### 案例

**案例1：用 breakpoint() 调试**

```python
def calculate(a, b):
    result = a * b
    breakpoint()          # 此处暂停，可输入 p a, p b, n...
    return result / 2

calculate(10, 5)
```

**案例2：条件断点——只在特定条件下暂停**

```python
for i in range(100):
    if i == 50:
        breakpoint()       # 只在 i==50 时暂停
    print(i)
```

**案例3：生产环境安全——按环境变量决定是否调试**

```python
import os

def debug_hook():
    if os.getenv("DEBUG") == "1":
        breakpoint()       # 只有设置了 DEBUG=1 才会暂停
    # 生产环境不设这个变量，断点自动跳过

def critical_operation(data):
    debug_hook()
    return data * 2
```

---

## 1.4 代码质量工具

### 理论：格式化 vs 检查 vs 类型检查

| 工具 | 做什么 | 类比 |
|------|--------|------|
| black/ruff format | 统一代码格式（缩进、引号、换行） | 自动排版 |
| ruff check | 找出潜在 bug 和不良写法 | 语法校对 |
| mypy | 检查类型标注是否正确 | 类型审查 |

---

### 案例

**案例1：black 自动格式化**

```bash
pip install black
black .                        # 格式化整个目录
black --check .                # 只检查不修改（CI 中用）
```

**案例2：ruff 一站式检查 + 修复**

```bash
pip install ruff
ruff check .                   # 检查问题
ruff check --fix .             # 自动修复
ruff format .                  # 格式化
```

**案例3：pyproject.toml 统一配置**

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "B", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 本章速查

| 命令 | 做什么 |
|------|--------|
| `python --version` | 查看版本 |
| `python -m venv .venv` | 创建虚拟环境 |
| `source .venv/bin/activate` | 激活 |
| `deactivate` | 退出 |
| `pip install pkg` | 安装包 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `breakpoint()` | 设断点 |
| `black .` | 格式化代码 |
| `ruff check .` | 代码检查 |
