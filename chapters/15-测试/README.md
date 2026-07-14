# 第十五章：测试

---

## 理论：为什么要写测试？

每次改了代码，怎么知道没把别的东西搞坏？靠测试。

- **没有测试**：改了代码 → 手动点点看 → "好像没问题" → 上线 → 炸了
- **有测试**：改了代码 → 跑 `pytest` → 3秒后看到红/绿 → 绿了安心上线

测试分几个层次：
- **单元测试**：测单个函数/方法（本题）
- **集成测试**：测多个模块协作
- **端到端测试**：模拟真实用户操作

---

### 关键字/语法

**unittest（内置）**：

```python
import unittest

class TestXXX(unittest.TestCase):
    def setUp(self):           # 每个测试前执行
        pass
    def tearDown(self):        # 每个测试后执行
        pass
    def test_something(self):  # 以 test_ 开头的方法
        self.assertEqual(a, b)
        self.assertTrue(cond)
        with self.assertRaises(TypeError):
            bad_code()
```

**pytest（推荐——更简洁）**：

```python
import pytest

def test_something():          # 函数名以 test_ 开头
    assert func(1, 2) == 3      # 直接用 assert！

def test_raises():
    with pytest.raises(ValueError, match="错误信息"):
        bad_code()
```

| pytest 核心功能 | 说明 |
|----------------|------|
| `@pytest.fixture` | 为测试准备依赖数据（自动注入） |
| `@pytest.mark.parametrize` | 一套测试跑多组数据 |
| `conftest.py` | 共享 fixture，pytest 自动发现 |
| `pytest -v` | 详细输出 |
| `pytest -k "pattern"` | 只跑名字匹配的测试 |
| `pytest --lf` | 只跑上次失败的（开发时的利器） |

---

### 案例

**案例1：pytest 基础——比 unittest 简洁得多**

```python
# test_math.py
import pytest

def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3
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
# pytest 自动跑3次！一次失败不影响其他
```

**案例3（工业级）：Mock——隔离外部依赖**

```python
from unittest.mock import Mock, patch

# 被测代码
def get_user_name(db, user_id):
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    return user.get("name", "Unknown") if user else "Unknown"

# 测试：不依赖真实数据库
def test_get_user_name():
    mock_db = Mock()
    mock_db.query.return_value = {"id": 1, "name": "Alice"}

    name = get_user_name(mock_db, 1)
    assert name == "Alice"
    mock_db.query.assert_called_once_with("SELECT * FROM users WHERE id=1")

def test_get_user_missing():
    mock_db = Mock()
    mock_db.query.return_value = None

    name = get_user_name(mock_db, 999)
    assert name == "Unknown"
```

**案例4：fixture——准备和清理测试数据**

```python
@pytest.fixture
def sample_users():
    """准备测试数据——多个测试可以共用"""
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
    ]
    yield data    # 传给测试函数
    # yield 之后 = 清理代码
    print("清理完成")

def test_filter_adults(sample_users):
    adults = [u for u in sample_users if u["age"] >= 18]
    assert len(adults) == 2
```

---

## 本章速查

| 概念 | 说明 |
|------|------|
| `unittest` | 内置框架，Java 风格 |
| `pytest` | 事实标准，语法简洁 |
| `Mock` | 替代真实对象，验证调用行为 |
| `patch` | 临时替换模块中的对象 |
| `fixture` | 为测试准备可复用的数据 |
| `parametrize` | 一组测试参数跑多次 |
