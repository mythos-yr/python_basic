# 第十五章：测试

---

## 15.1 unittest 基础

### 知识点：TestCase 和断言方法

**案例1：unittest 的基本结构**

```python
import unittest

# 被测试的代码
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

# 测试类
class TestMathOperations(unittest.TestCase):
    """测试数学运算函数"""

    def setUp(self):
        """每个测试方法调用前执行——准备测试数据"""
        self.numbers = [1, 2, 3, 4, 5]
        print(f"  setUp: 准备数据 {self.numbers}")

    def tearDown(self):
        """每个测试方法调用后执行——清理资源"""
        print(f"  tearDown: 清理...")

    def test_add_positive(self):
        """测试正数相加"""
        self.assertEqual(add(1, 2), 3)
        self.assertEqual(add(0, 5), 5)
        # self.assertEqual(add(-1, 1), 1)  # 这行会失败

    def test_add_negative(self):
        """测试负数相加"""
        self.assertEqual(add(-1, -2), -3)

    def test_divide_by_zero(self):
        """测试除零异常"""
        with self.assertRaises(ValueError) as ctx:
            divide(10, 0)
        self.assertIn("除数不能为零", str(ctx.exception))

    def test_divide_normal(self):
        """测试正常除法"""
        self.assertAlmostEqual(divide(10, 3), 3.333333, places=5)


# 运行测试
if __name__ == "__main__":
    unittest.main()
```

**案例2：unittest 的各种断言方法**

```python
import unittest

class TestAssertions(unittest.TestCase):

    def test_all_asserts(self):
        # 相等性
        self.assertEqual(1 + 2, 3)             # a == b
        self.assertNotEqual(1, 2)

        # 布尔
        self.assertTrue("hello".isalpha())
        self.assertFalse("123".isalpha())

        # 身份和成员
        self.assertIs(None, None)              # a is b
        self.assertIsNot([], [])               # a is not b
        self.assertIn("a", ["a", "b", "c"])    # a in b
        self.assertNotIn("z", ["a", "b"])      # a not in b

        # 浮点数
        self.assertAlmostEqual(0.1 + 0.2, 0.3, places=7)

        # 异常
        with self.assertRaises(ZeroDivisionError):
            1 / 0

        # 大于/小于
        self.assertGreater(5, 3)
        self.assertLess(3, 5)
        self.assertGreaterEqual(5, 5)
```

**案例3：工业级 —— 参数化测试与测试套件**

```python
import unittest
from typing import List, Tuple

def is_valid_email(email: str) -> bool:
    """验证邮箱格式"""
    import re
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

class TestEmailValidation(unittest.TestCase):
    """邮箱验证测试（参数化写法）"""

    # 参数化：用 subTest 避免一个失败导致后续都不执行
    def test_valid_emails(self):
        valid_cases = [
            "user@example.com",
            "user.name@example.co.uk",
            "user+tag@example.org",
            "123@test.com",
        ]
        for email in valid_cases:
            with self.subTest(email=email):
                self.assertTrue(is_valid_email(email), f"{email} 应该是有效的")

    def test_invalid_emails(self):
        invalid_cases = [
            "",
            "not_an_email",
            "@missing_user.com",
            "user@",
            "user@.com",
            "user name@example.com",
        ]
        for email in invalid_cases:
            with self.subTest(email=email):
                self.assertFalse(is_valid_email(email), f"{email} 应该是无效的")


# 自定义测试套件加载器
def create_suite():
    """创建测试套件"""
    suite = unittest.TestSuite()
    suite.addTest(TestEmailValidation("test_valid_emails"))
    suite.addTest(TestEmailValidation("test_invalid_emails"))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(create_suite())
```

---

## 15.2 pytest —— Python 测试的事实标准

### 知识点：pytest 的优势与核心功能

**案例1：pytest 的简洁语法**

```python
# test_calculator.py
import pytest

# 被测试的代码
class Calculator:
    def add(self, a, b):
        return a + b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("除数不能为零")
        return a / b

# ===== pytest 测试 =====
# 注意：不需要继承 TestCase，不需要 self！

def test_add():
    """函数名以 test_ 开头即可"""
    calc = Calculator()
    assert calc.add(1, 2) == 3       # 直接用 assert！
    assert calc.add(-1, -2) == -3

def test_divide():
    calc = Calculator()
    assert calc.divide(10, 2) == 5.0

def test_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError, match="除数不能为零"):
        calc.divide(10, 0)

# 运行:
# pytest test_calculator.py
# pytest test_calculator.py -v        # 详细输出
# pytest test_calculator.py -s        # 显示 print 输出
```

**案例2：pytest fixture —— 准备和清理测试数据**

```python
import pytest
import tempfile
import os

# fixture: 自动注入测试依赖
@pytest.fixture
def calculator():
    """创建一个 Calculator 实例（每个测试函数调用时创建新的）"""
    print("\n  [fixture] 创建 Calculator")
    return Calculator()

@pytest.fixture
def temp_file():
    """创建临时文件，测试结束后自动删除"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("test data\nline 2\n")
        filepath = f.name

    yield filepath              # 传给测试函数

    # yield 之后的代码 = tearDown
    os.unlink(filepath)
    print(f"\n  [fixture] 删除临时文件: {filepath}")

# 使用 fixture
def test_with_calc(calculator):    # fixture 名称作为参数自动注入
    assert calculator.add(3, 4) == 7

def test_with_file(temp_file):
    with open(temp_file) as f:
        content = f.read()
    assert "test data" in content


# fixture 的 scope 控制
@pytest.fixture(scope="module")    # 整个测试模块共享一个实例（只创建一次）
def heavy_resource():
    """模拟昂贵资源（数据库连接等）——整个模块复用"""
    print("\n  [fixture module] 创建昂贵资源（只一次）")
    resource = {"connected": True, "data": []}
    yield resource
    print("\n  [fixture module] 释放资源")
```

**案例3：工业级 —— mock 隔离外部依赖**

```python
import pytest
from unittest.mock import Mock, patch, MagicMock

# 被测试的代码
class UserService:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_name(self, user_id: int) -> str:
        """从数据库获取用户名"""
        user = self.db.query(f"SELECT * FROM users WHERE id = {user_id}")
        if user is None:
            raise ValueError(f"用户 {user_id} 不存在")
        return user.get("name", "Unknown")

    def send_welcome_email(self, email: str) -> bool:
        """发送欢迎邮件（调用外部邮件服务）"""
        # import smtplib
        # server = smtplib.SMTP("smtp.example.com")
        # return server.sendmail(...)
        return True  # 简化


class TestUserService:
    """测试 UserService——mock 掉数据库和邮件服务"""

    @pytest.fixture
    def mock_db(self):
        """mock 数据库连接"""
        db = Mock()
        # 配置 mock 的行为
        db.query.return_value = {"id": 1, "name": "Alice", "email": "alice@example.com"}
        return db

    @pytest.fixture
    def user_service(self, mock_db):
        return UserService(mock_db)

    def test_get_user_name(self, user_service, mock_db):
        """测试获取用户名"""
        name = user_service.get_user_name(1)
        assert name == "Alice"

        # 验证 mock 是否被正确调用
        mock_db.query.assert_called_once_with("SELECT * FROM users WHERE id = 1")

    def test_get_user_not_found(self, mock_db):
        """测试用户不存在的情况"""
        mock_db.query.return_value = None
        service = UserService(mock_db)

        with pytest.raises(ValueError, match="不存在"):
            service.get_user_name(999)

    @patch("smtplib.SMTP")   # patch 掉真实的 SMTP 连接
    def test_send_email(self, mock_smtp, user_service):
        """测试发送邮件——不会真正发送"""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_server.sendmail.return_value = {}

        # result = user_service.send_welcome_email("alice@example.com")
        # assert result is True
        # mock_server.sendmail.assert_called_once()


# 参数化测试（pytest 的杀手锏功能）
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])
def test_add_parametrized(a, b, expected):
    """四条测试用例，pytest 自动运行四次"""
    assert a + b == expected


# 运行命令:
# pytest test_module.py -v          # 详细
# pytest test_module.py -k "test_add"  # 只运行名字包含 test_add 的
# pytest test_module.py --cov=src   # 带覆盖率（需要 pytest-cov）
# pytest test_module.py -x          # 遇到第一个失败即停止
```

---

## 15.3 测试覆盖率与 CI 集成

**案例1：使用 pytest-cov 查看覆盖率**

```bash
# 安装
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=my_package --cov-report=html

# 终端报告（简略）
pytest --cov=my_package --cov-report=term-missing

# 输出示例:
# Name                    Stmts   Miss  Cover   Missing
# -------------------------------------------------------
# my_package/__init__.py      5      0   100%
# my_package/core.py         45     12    73%   23-28, 45-50
# my_package/utils.py        20      3    85%   15, 22, 31
# -------------------------------------------------------
# TOTAL                      70     15    79%
```

**案例2：GitHub Actions CI 配置**

```yaml
# .github/workflows/test.yml
name: Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e ".[dev,test]"

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

**案例3：工业级 —— 测试数据工厂**

```python
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

class UserFactory:
    """
    测试数据工厂。
    避免在每个测试中重复编写创建用户数据的代码。
    """

    _id_counter = 0

    @classmethod
    def build(cls, **overrides) -> Dict[str, Any]:
        """构建一个用户字典（根据需要覆盖字段）"""
        cls._id_counter += 1
        defaults = {
            "id": cls._id_counter,
            "name": f"user_{cls._id_counter}",
            "email": f"user_{cls._id_counter}@test.com",
            "age": 25,
            "is_active": True,
            "created_at": datetime.now(),
        }
        defaults.update(overrides)
        return defaults

    @classmethod
    def build_batch(cls, count: int, **overrides) -> list:
        """批量构建"""
        return [cls.build(**overrides) for _ in range(count)]


class OrderFactory:
    """订单测试数据工厂"""

    @classmethod
    def build(cls, **overrides) -> Dict[str, Any]:
        defaults = {
            "order_id": f"ORD-{hash(str(datetime.now()))}"[:12],
            "user_id": 1,
            "amount": 99.99,
            "status": "pending",
            "created_at": datetime.now(),
        }
        defaults.update(overrides)
        return defaults


# 在测试中使用工厂
def test_user_activation():
    """测试用户激活逻辑"""
    user = UserFactory.build(is_active=False, age=17)
    assert user["is_active"] is False
    assert user["age"] == 17

def test_batch_processing():
    """测试批量处理"""
    users = UserFactory.build_batch(100, is_active=True)
    assert len(users) == 100
    assert all(u["is_active"] for u in users)
```

---

## 本章速查

| 框架 | 特点 |
|------|------|
| `unittest` | 内置，Java 风格，适合简单测试 |
| `pytest` | 事实标准，语法简洁，插件丰富 |

| pytest 命令 | 作用 |
|-------------|------|
| `pytest -v` | 详细输出 |
| `pytest -k "pattern"` | 只运行匹配模式的测试 |
| `pytest -x` | 遇到失败立即停止 |
| `pytest --cov=src` | 带覆盖率报告 |
| `pytest -s` | 显示 print 输出 |
| `pytest --lf` | 只运行上次失败的测试 |

| 关键概念 | 说明 |
|----------|------|
| `@pytest.fixture` | 准备测试依赖，自动注入 |
| `@pytest.mark.parametrize` | 一个测试跑多组数据 |
| `Mock / patch` | 隔离外部依赖（数据库、网络、文件系统） |
| `conftest.py` | 共享 fixture，pytest 自动加载 |
