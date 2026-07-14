# 第十五章：测试

---

## 理论：为什么要写测试？

每次改了代码，怎么知道没把别的东西搞坏？靠测试。

- **没有测试**：改代码 → 手动点点 → "好像没问题" → 上线 → 炸了
- **有测试**：改代码 → 跑 `pytest` → 3 秒绿了 → 放心上线

**测试三层**：单元测试（测函数）→ 集成测试（测模块协作）→ 端到端测试（模拟用户）。

---

## 15.1 unittest——内置框架

### 关键字/语法

```python
import unittest

class TestMath(unittest.TestCase):
    def setUp(self):                          # 每个 test_ 方法前执行
        self.data = [1, 2, 3, 4, 5]

    def tearDown(self):                       # 每个 test_ 方法后执行
        pass

    def test_sum(self):                       # 方法名必须以 test_ 开头
        self.assertEqual(sum(self.data), 15)
        self.assertTrue(sum(self.data) > 0)
        self.assertIn(3, self.data)

    def test_raises(self):
        with self.assertRaises(ZeroDivisionError):
            1 / 0

if __name__ == "__main__":
    unittest.main()
```

### 常用断言方法

| 断言 | 检查 |
|------|------|
| `assertEqual(a, b)` | a == b |
| `assertTrue(x)` | bool(x) is True |
| `assertFalse(x)` | bool(x) is False |
| `assertIs(a, b)` | a is b |
| `assertIn(a, b)` | a in b |
| `assertRaises(Error)` | 抛出指定异常 |
| `assertAlmostEqual(a, b)` | 浮点数近似相等 |

---

## 15.2 pytest——Python 测试的事实标准

### 关键字/语法

pytest 比 unittest 简洁得多：不需要 TestCase 类，直接用 `assert`。

```bash
pytest                          # 自动发现并运行所有测试
pytest -v                       # 详细输出
pytest -k "pattern"             # 只跑名字匹配的测试
pytest test_file.py::test_func  # 只跑指定函数
pytest --lf                     # 只跑上次失败的（开发利器）
pytest -x                       # 遇到第一个失败就停
pytest --cov=src                # 带覆盖率（需 pytest-cov）
```

**核心功能**：

| 功能 | 语法 | 用途 |
|------|------|------|
| fixture | `@pytest.fixture` | 为测试准备可复用数据 |
| parametrize | `@pytest.mark.parametrize` | 一套测试跑多组数据 |
| conftest.py | 项目根目录下的文件 | 共享 fixture，pytest 自动发现 |
| Mock | `unittest.mock.Mock` | 替代真实依赖（数据库、网络） |
| patch | `unittest.mock.patch` | 临时替换模块中的对象 |

---

### 案例

**案例1：pytest 基础——简洁对比 unittest**

```python
# test_calc.py
import pytest

def add(a, b): return a + b

def test_add():
    assert add(1, 2) == 3           # 直接用 assert！
    assert add(-1, -2) == -3

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

**案例2：参数化——一个测试跑多组数据**

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("Python", "PYTHON"),
])
def test_upper(input, expected):
    assert input.upper() == expected
# pytest 自动跑 3 次！一次失败不影响其他
```

**案例3：Mock——不依赖真实数据库**

```python
from unittest.mock import Mock

def get_user(db, uid):
    row = db.query(f"SELECT * FROM users WHERE id={uid}")
    return row.get("name", "Unknown")

def test_get_user():
    mock_db = Mock()
    mock_db.query.return_value = {"id": 1, "name": "Alice"}

    assert get_user(mock_db, 1) == "Alice"
    mock_db.query.assert_called_once_with("SELECT * FROM users WHERE id=1")
```

**案例4：fixture——准备和清理测试数据**

```python
@pytest.fixture
def sample_data():
    data = [{"name": "Alice"}, {"name": "Bob"}]   # setup
    yield data                                      # 传给测试
    print("cleanup")                                # teardown

def test_with_fixture(sample_data):
    assert len(sample_data) == 2
```

---

## 15.3 测试覆盖率

```bash
pip install pytest-cov

pytest --cov=my_package --cov-report=term-missing
# 输出每个文件的覆盖率，标注哪些行没被测试覆盖
```

---

## 本章速查

| 概念 | 说明 |
|------|------|
| `unittest` | 内置框架，TestCase 子类 + assertXxx 方法 |
| `pytest` | 事实标准，直接 `assert`，fixture + parametrize |
| `Mock` | 替代真实对象，可验证调用行为和参数 |
| `patch` | 临时替换模块中的对象 |
| `fixture` | 可复用的测试数据准备 |
| `parametrize` | 一套代码跑多组输入 |
