# 第一章：环境搭建与工具链

---

## 1.1 Python 解释器

### 理论：Python 代码是怎么跑起来的？

你写的 `.py` 文件 → Python 把它**编译成字节码** → **Python虚拟机（PVM）**逐条执行字节码。

**类比**：菜谱（源代码）→ 翻译成厨师能懂的标准化指令（字节码）→ 厨师做菜（虚拟机执行）。

**字节码**是中间表示，存在 `.pyc` 文件中。每次运行 `.py`，Python 先检查是否需要重新编译。如果 `.py` 没变，直接用缓存的 `.pyc`。

**Python 是一种语言规范**，有多种解释器实现：

| 解释器 | 特点 | 适合 |
|--------|------|------|
| **CPython** | 官方实现，C 语言写，生态最全 | 99% 的开发 |
| **PyPy** | JIT 编译，运行速度快 4-5 倍 | 长时间计算任务 |
| **Jython** | 跑在 JVM 上，可调 Java 类库 | 和 Java 集成 |

---

### 关键字/命令

| 命令 | 作用 |
|------|------|
| `python` | 启动交互式解释器（`>>>` 提示符） |
| `python file.py` | 执行脚本 |
| `python -c "print(1+2)"` | 执行一行代码 |
| `python -m module` | 把模块当脚本运行（Python 自动在 sys.path 中搜索） |

**`python -m` 的常用场景**：

```bash
python -m http.server 8000      # 当前目录变静态文件服务器
python -m json.tool             # JSON 格式化
python -m pip install flask     # 即使 pip 命令没配好也能用
python -m venv .venv            # 创建虚拟环境
```

**`sys` 模块——在代码中获取解释器信息**：

```python
import sys
print(sys.version)          # 完整版本信息
print(sys.executable)       # 当前 python 可执行文件路径
print(sys.path)             # 模块搜索路径列表
print(sys.modules)          # 已加载的模块缓存字典
```

---

### 案例

**案例1：查看当前解释器信息**

```python
import sys, platform

print(f"版本: {sys.version_info.major}.{sys.version_info.minor}")
print(f"实现: {platform.python_implementation()}")   # CPython
print(f"路径: {sys.executable}")
print(f"64位: {sys.maxsize > 2**32}")
```

**案例2：查看代码编译后的字节码（理解执行原理）**

```python
import dis

def add(a, b):
    return a + b

dis.dis(add)
# LOAD_FAST    0 (a)     ← 把 a 加载到栈
# LOAD_FAST    1 (b)     ← 把 b 加载到栈
# BINARY_OP    0 (+)     ← 做加法
# RETURN_VALUE           ← 返回结果
```

**案例3：compile + exec——理解"编译和执行是分开的"**

```python
source = "x = 10\ny = 20\nresult = x + y"
code = compile(source, "<demo>", "exec")  # 编译源码 → 字节码对象
namespace = {}
exec(code, namespace)                      # 在指定命名空间中执行
print(namespace["result"])                 # 30
```

---

## 1.2 虚拟环境 (venv)

### 理论：为什么需要虚拟环境？

项目A 需要 `requests==2.20`，项目B 需要 `requests==2.28`。全局只能装一个版本 → 冲突。

**虚拟环境 = 给每个项目一个独立的包安装空间**，各自隔离，互不干扰。

**类比**：全局环境 = 公共图书馆（谁都在里面放书，乱）；虚拟环境 = 每个项目自带小书架。

**虚拟环境不是完整复制 Python**——它只是一个独立目录，有自己的 `site-packages`。解释器本身还是共享的。

---

### 关键字/命令

```bash
# 创建
python -m venv .venv

# 激活 (macOS/Linux)
source .venv/bin/activate

# 激活 (Windows)
.venv\Scripts\activate

# 激活后终端 prompt 前出现 (.venv)，pip install 只作用于当前环境

# 退出
deactivate
```

**pip 命令速查**：

| 命令 | 作用 |
|------|------|
| `pip install pkg` | 安装最新版 |
| `pip install pkg==1.2.3` | 安装指定版本 |
| `pip install "pkg>=2.0,<3.0"` | 版本范围 |
| `pip uninstall pkg -y` | 卸载 |
| `pip list` | 列出已安装 |
| `pip list --outdated` | 哪些包有新版本 |
| `pip show pkg` | 查看包详细信息 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `pip install -r requirements.txt` | 从文件安装依赖 |
| `pip check` | 检查依赖冲突 |

---

### 案例

**案例1：创建和使用虚拟环境完整流程**

```bash
python -m venv .venv           # 1. 创建
source .venv/bin/activate      # 2. 激活
which python                    # 3. 验证 → 应指向 .venv/bin/python
pip list                        # 4. 初始几乎为空
pip install requests pandas     # 5. 安装依赖
pip freeze > requirements.txt  # 6. 导出
deactivate                      # 7. 退出
```

**案例2：验证是否在虚拟环境中**

```python
import sys
print(sys.prefix != sys.base_prefix)  # True = 在虚拟环境中
```

**案例3：在新环境一键复现一模一样的环境**

```bash
# 开发机导出精确版本
pip freeze > requirements-lock.txt

# 服务器/同事机器上安装完全相同的版本
pip install -r requirements-lock.txt
```

---

## 1.3 调试器 (pdb)

### 理论：程序跑太快了，让它在某一行"暂停"

pdb 让程序在任意行暂停，你可以检查所有变量的值，然后逐行执行。

---

### 关键字/命令

```python
breakpoint()   # Python 3.7+：在代码中设断点
```

**进入 pdb 后最常用的 5 个命令**：

| 命令 | 全称 | 作用 |
|------|------|------|
| `n` | next | 执行下一行 |
| `s` | step | 步入函数内部 |
| `c` | continue | 继续执行直到下一个断点 |
| `p 变量名` | print | 打印变量值 |
| `q` | quit | 退出调试 |

---

### 案例

**案例1：基本断点调试**

```python
def calculate(a, b):
    result = a * b
    breakpoint()          # 程序在此暂停 → 输入 p a, p b, n...
    return result / 2

calculate(10, 5)
```

**案例2：条件断点——只在满足条件时暂停**

```python
for i in range(1000):
    if i == 500:
        breakpoint()       # 只在 i 为 500 时暂停
    # ... 正常处理
```

**案例3（工业级）：按环境变量控制——生产环境不会误触发**

```python
import os

def debug_hook():
    if os.getenv("DEBUG") == "1":
        breakpoint()       # DEBUG=1 时才暂停；生产环境不设此变量
```

---

## 1.4 代码质量工具

### 知识点

| 工具 | 做什么 | 类比 |
|------|--------|------|
| black | 自动格式化代码（缩进、引号、换行） | 自动排版 |
| ruff | 检查代码问题（未用的变量、可能 bug）+ 格式化 | 语法校对 + 排版 |
| mypy | 检查类型注解是否正确 | 类型审查 |

```bash
pip install black ruff mypy

black .                           # 格式化整个目录
black --check .                   # 只检查不改（CI 中用）
ruff check .                      # 检查问题
ruff check --fix .                # 自动修复
ruff format .                     # 格式化
mypy src/                         # 类型检查
```

**pyproject.toml 统一配置**：

```toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "W", "F", "I", "N", "B", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
```

---

## 本章速查

| 命令 | 做什么 |
|------|--------|
| `python --version` | 查看版本 |
| `python -c "code"` | 执行一行代码 |
| `python -m venv .venv` | 创建虚拟环境 |
| `source .venv/bin/activate` | 激活 |
| `deactivate` | 退出 |
| `pip install pkg` | 安装包 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `breakpoint()` | 设断点 |
| `black .` | 格式化代码 |
