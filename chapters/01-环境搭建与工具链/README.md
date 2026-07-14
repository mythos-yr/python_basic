# 第一章：环境搭建与工具链

---

## 1.1 Python 解释器

### 知识点：CPython vs PyPy vs Jython

Python 是一种**语言规范**，有多种解释器实现：

| 解释器 | 特点 | 适用场景 |
|--------|------|----------|
| CPython | 官方实现，C 语言编写，生态最全 | 通用开发 |
| PyPy | JIT 编译，执行速度快 4-5 倍 | 长时间运行的计算密集型任务 |
| Jython | 跑在 JVM 上，可调用 Java 类库 | 与 Java 生态集成 |

**案例1：查看当前使用的解释器**

```python
import sys
import platform

# 查看解释器类型和版本
print(f"解释器: {sys.implementation.name}")     # 解释器: cpython
print(f"版本: {sys.version}")                    # 完整版本信息
print(f"平台: {platform.python_implementation()}")  # CPython

# 查看解释器可执行文件路径
print(f"解释器路径: {sys.executable}")
```

**案例2：验证 PyPy 的速度优势（需要在 PyPy 环境下运行）**

```python
import time

def fibonacci(n):
    """纯计算密集型任务"""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

start = time.perf_counter()
result = fibonacci(35)
elapsed = time.perf_counter() - start
print(f"fibonacci(35) = {result}, 耗时: {elapsed:.2f}s")
# CPython 约 2-4 秒
# PyPy 约 0.5-1 秒（JIT 预热后）
```

**案例3：判断当前解释器类型（兼容性检查）**

```python
import sys
import platform

def get_interpreter_info():
    """工业级：获取解释器完整信息，用于日志和调试"""
    impl = sys.implementation
    info = {
        "name": impl.name,
        "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
        "build_date": platform.python_build()[1],
        "is_64bit": sys.maxsize > 2**32,
        "gil_enabled": sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True,
    }
    return info

for key, value in get_interpreter_info().items():
    print(f"{key}: {value}")
```

---

### 知识点：Python 2.x 与 3.x 的核心差异

**案例1：print 语句 vs 函数**

```python
# Python 2:
# print "hello"          # 语句，不需要括号

# Python 3:
print("hello")            # 函数，必须加括号
print("a", "b", "c", sep="|", end=".\n")  # 支持 sep 和 end 参数
# 输出: a|b|c.
```

**案例2：整数除法的行为差异**

```python
# Python 2:
# 5 / 2   → 2    （整数除法默认截断）
# 5 // 2  → 2
# 5 / 2.0 → 2.5

# Python 3:
print(5 / 2)     # 2.5  （/ 始终返回浮点数）
print(5 // 2)    # 2    （// 才是整除）
print(5 / 2.0)   # 2.5
```

**案例3：Unicode 字符串处理差异**

```python
# Python 2: str 是 bytes，unicode 是单独的字符串类型
# Python 3: str 就是 Unicode 字符串

# Python 3 中所有字符串都是 Unicode
text = "你好，世界"                      # 直接支持中文
print(len(text))                         # 5 (5个字符，不是字节数)
print(text.encode("utf-8"))              # b'\xe4\xbd\xa0\xe5\xa5\xbd...'
print(text.encode("utf-8").decode("utf-8"))  # 还原: 你好，世界

# range 行为也改变了
r = range(10)
print(type(r))   # <class 'range'>  —— 可迭代对象，不是列表
print(list(r))   # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
```

---

### 知识点：解释器的工作原理

Python 代码的执行过程：**源代码 → 字节码(.pyc) → PVM（Python 虚拟机）执行**

**案例1：查看字节码**

```python
import dis

def add(a, b):
    return a + b

# 反汇编查看字节码指令
dis.dis(add)
# 输出类似:
#   2 LOAD_FAST    0 (a)
#   4 LOAD_FAST    1 (b)
#   6 BINARY_OP    0 (+)
#  10 RETURN_VALUE
```

**案例2：手动编译和执行字节码**

```python
import dis

source_code = """
x = 10
y = 20
result = x + y
"""

# 编译成字节码
code_object = compile(source_code, "<string>", "exec")

# 查看编译后的字节码
dis.dis(code_object)

# 执行字节码
exec(code_object)
print(result)  # 30
```

**案例3：工业级——使用 compile 实现安全的表达式求值**

```python
import ast
import operator

class SafeEvaluator:
    """
    安全的数学表达式求值器。
    只允许白名单中的操作符和节点类型，防止代码注入。
    """
    # 白名单：只允许安全的操作
    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp,
        ast.Constant, ast.Load,
    )

    @classmethod
    def evaluate(cls, expression: str) -> float:
        """安全地对数学表达式求值"""
        try:
            tree = ast.parse(expression.strip(), mode="eval")
        except SyntaxError as e:
            raise ValueError(f"语法错误: {e}")

        # 校验 AST 节点是否都在白名单中
        for node in ast.walk(tree):
            if not isinstance(node, cls.ALLOWED_NODES):
                raise ValueError(f"不安全的操作: {type(node).__name__}")

        code = compile(tree, "<safe_eval>", "eval")
        return eval(code, {"__builtins__": {}}, {})

    # 注意：这里的 operator 白名单未直接在 eval 中使用，
    # 是因为 compile 后的字节码已经绑定了 Python 原生的操作符语义

# 使用
print(SafeEvaluator.evaluate("3 + 5 * 2"))     # 13.0
print(SafeEvaluator.evaluate("2 ** 10"))       # 1024.0
```

---

### 知识点：`python -m` 的用法

`-m` 参数将一个模块当做脚本来运行，Python 会自动在 `sys.path` 中搜索该模块。

**案例1：常用模块的 -m 调用**

```bash
# 启动 HTTP 服务器（当前目录作为静态文件服务器）
python -m http.server 8000

# JSON 格式化工具
echo '{"name":"Alice","age":30}' | python -m json.tool

# 查看 pip 版本
python -m pip --version

# 代码检查（需要安装 flake8）
python -m flake8 my_script.py
```

**案例2：理解 -m 对 sys.path 的影响**

```python
# 文件: demo_module.py
import sys

if __name__ == "__main__":
    print("作为脚本直接运行")
    print(f"sys.path[0] = {sys.path[0]}")

# 运行方式:
# python demo_module.py          → sys.path[0] 是文件所在目录
# python -m demo_module          → sys.path[0] 是当前工作目录
```

**案例3：工业级——用 -m 统一项目入口，避免导入路径问题**

```python
# 项目结构:
# myproject/
#   __init__.py
#   cli.py       ← 命令行入口
#   core/
#     __init__.py
#     engine.py

# cli.py 中:
import argparse
from .core.engine import run

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(args.config)

if __name__ == "__main__":
    main()

# 运行方式:
# cd myproject/..
# python -m myproject.cli --config config.yaml  ← 正确
# python myproject/cli.py --config config.yaml  ← 相对导入会失败
```

---

## 1.2 环境管理

### 知识点：pip 包管理

**案例1：pip 基础操作**

```bash
# 安装包
pip install requests

# 安装指定版本
pip install requests==2.28.0

# 卸载包
pip uninstall requests -y

# 列出已安装的包
pip list

# 导出当前环境的依赖
pip freeze > requirements.txt

# 从文件安装依赖
pip install -r requirements.txt

# 查看包的详细信息
pip show requests
```

**案例2：pip 的依赖冲突检测**

```bash
# 检查依赖兼容性
pip check

# 安装时查看将要安装的依赖
pip install --dry-run pandas

# 列出过期的包
pip list --outdated

# 查看包的依赖树（需要 pip install pipdeptree）
pipdeptree
```

**案例3：工业级——锁定依赖版本的策略**

```bash
# 1. 开发阶段：记录宽松依赖
cat > setup.cfg << 'EOF'
[options]
install_requires =
    requests>=2.28,<3.0
    numpy>=1.24,<2.0
    pandas>=2.0,<3.0
EOF

# 2. 发布前：锁定精确版本
pip freeze > requirements-lock.txt

# 3. 生产部署：只安装锁定版本
pip install -r requirements-lock.txt

# 4. 安全审计：检查已知漏洞
pip install safety
safety check
```

---

### 知识点：虚拟环境 (venv)

**案例1：虚拟环境的创建和使用**

```bash
# 创建虚拟环境
python -m venv myproject_env

# 激活（macOS/Linux）
source myproject_env/bin/activate

# 激活（Windows）
# myproject_env\Scripts\activate

# 此时 prompt 前会出现 (myproject_env)
# 现在 pip install 的任何包只会装在这个环境中

# 退出虚拟环境
deactivate
```

**案例2：用脚本验证虚拟环境隔离性**

```python
import sys
import site

def check_environment():
    """检查当前 Python 环境的隔离状态"""
    print(f"Python 路径: {sys.executable}")
    print(f"是否是虚拟环境: {sys.prefix != sys.base_prefix}")
    print(f"site-packages 路径: {site.getsitepackages()}")

    # 如果是虚拟环境，site-packages 在 env/ 目录下
    # 如果是全局环境，site-packages 在系统路径下

check_environment()
```

**案例3：工业级——项目的环境初始化脚本**

```bash
#!/bin/bash
# 文件: setup_env.sh —— 一键初始化开发环境

set -e

PROJECT_NAME="myproject"
PYTHON_VERSION="3.11"

echo "=== 创建虚拟环境 ==="
python${PYTHON_VERSION} -m venv .venv

echo "=== 激活虚拟环境 ==="
source .venv/bin/activate

echo "=== 升级 pip ==="
pip install --upgrade pip setuptools wheel

echo "=== 安装开发依赖 ==="
pip install -e ".[dev,test]"

echo "=== 安装 pre-commit hooks ==="
pre-commit install

echo "=== 环境初始化完成 ==="
echo "运行: source .venv/bin/activate"
```

---

## 1.3 开发工具

### 知识点：调试器

**案例1：pdb 命令行调试**

```python
import pdb

def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    pdb.set_trace()        # ← 程序在此处暂停，进入调试模式
    # 常用命令: n(下一行), s(步入), c(继续), p var(打印变量), l(查看代码)
    return total / count

result = calculate_average([10, 20, 30, 40])
print(result)
```

**案例2：breakpoint() 断点调试（Python 3.7+）**

```python
def process_data(items):
    results = []
    for i, item in enumerate(items):
        processed = item * 2
        if processed > 100:
            # Python 3.7+ 推荐的断点方式，比 pdb.set_trace() 更简洁
            breakpoint()  # 等同于 pdb.set_trace()
        results.append(processed)
    return results

data = [10, 30, 60, 80]
output = process_data(data)
print(output)
```

**案例3：工业级——通过环境变量控制调试行为**

```python
import os
import sys

def debug_hook():
    """
    根据环境变量决定调试行为。
    生产环境不会误触断点。
    """
    debug_mode = os.getenv("DEBUG", "0")

    if debug_mode == "1":
        # 开发环境：进入标准 pdb
        import pdb; pdb.set_trace()
    elif debug_mode == "pudb":
        # 开发环境：使用更友好的 pudb（需安装）
        import pudb; pudb.set_trace()
    elif debug_mode == "ipdb":
        # 开发环境：使用 ipdb（需安装）
        import ipdb; ipdb.set_trace()
    # 生产环境：debug_mode=0，什么都不做

def critical_operation(data):
    """关键业务函数"""
    debug_hook()  # 只在 DEBUG=1 时才会暂停
    # ... 正常业务逻辑 ...
    return data * 2

print(critical_operation(10))
```

---

### 知识点：代码格式化

**案例1：black 自动格式化**

```python
# 格式化前的代码（故意写乱）:
def foo(  x,y  ):
    return    x+y*  2

result=[foo(i,i+1)for i in range(10)]

# 运行: black script.py
# 格式化后:
def foo(x, y):
    return x + y * 2


result = [foo(i, i + 1) for i in range(10)]
```

**案例2：ruff 一站式代码检查与修复**

```bash
# 安装
pip install ruff

# 检查代码问题
ruff check .

# 自动修复能修复的问题
ruff check --fix .

# 同时检查和格式化
ruff format .

# 在 CI 中使用（严格模式）
ruff check --select=E,F,I,N,W --ignore=E501 .
```

**案例3：工业级——pyproject.toml 中统一配置格式化工具**

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # Pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]   # 允许未使用的导入

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

---

## 本章速查

| 命令 | 作用 |
|------|------|
| `python --version` | 查看 Python 版本 |
| `python -m venv .venv` | 创建虚拟环境 |
| `source .venv/bin/activate` | 激活虚拟环境 (macOS/Linux) |
| `pip install <pkg>` | 安装包 |
| `pip freeze > requirements.txt` | 导出依赖 |
| `python -m pdb script.py` | 命令行调试 |
| `black .` | 格式化代码 |
| `ruff check .` | 代码检查 |
