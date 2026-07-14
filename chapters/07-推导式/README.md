# 第七章：推导式 —— Python 最优雅的语法

---

## 7.1 列表推导式

### 知识点：基础语法——from 循环到推导式

**案例1：同一种逻辑的四种写法对比**

```python
# 需求: 对0-9的偶数求平方

# 方式1: 传统 for 循环
result1 = []
for i in range(10):
    if i % 2 == 0:
        result1.append(i ** 2)

# 方式2: map + filter
result2 = list(map(lambda x: x**2, filter(lambda x: x % 2 == 0, range(10))))

# 方式3: 列表推导式（最 Pythonic）
result3 = [i**2 for i in range(10) if i % 2 == 0]

# 方式4: 生成器表达式 + list()
result4 = list(i**2 for i in range(10) if i % 2 == 0)

print(result1 == result2 == result3 == result4)  # True
print(result3)  # [0, 4, 16, 36, 64]
```

**案例2：if 在 for 后（过滤）vs if-else 在 for 前（映射）**

```python
nums = [1, 2, 3, 4, 5, 6]

# if 在 for 后 = 过滤（不满足条件的直接扔掉）
evens = [x for x in nums if x % 2 == 0]
print(evens)  # [2, 4, 6]  ← 元素数量可能变少

# if-else 在 for 前 = 映射（每个元素都保留，但值可能改变）
labels = ["even" if x % 2 == 0 else "odd" for x in nums]
print(labels)  # ['odd', 'even', 'odd', 'even', 'odd', 'even']  ← 元素数量不变

# 记忆技巧：
# - for 后的 if → FILTER（过滤器）
# - for 前的 if-else → MAP（变换器，必须带 else）
```

**案例3：工业级 —— 数据清洗管道（推导式组合）**

```python
from typing import List, Dict, Optional
import re

class DataCleaner:
    """数据清洗器——多个推导式串联成处理管道"""

    @staticmethod
    def clean_phone_numbers(raw_data: List[str]) -> List[str]:
        """
        清洗手机号列表：去除非数字 → 过滤空值 → 去重 → 按格式分类。
        每一步都用推导式，清晰可读。
        """
        # 步骤1: 提取纯数字（过滤空白和无效字符）
        cleaned = [
            re.sub(r"\D", "", phone)
            for phone in raw_data
        ]

        # 步骤2: 过滤掉长度不对和非1开头的
        valid = [
            p for p in cleaned
            if len(p) == 11 and p.startswith("1")
        ]

        # 步骤3: 去重（保持顺序）
        seen = set()
        unique = [
            p for p in valid
            if not (p in seen or seen.add(p))
        ]

        return unique

    @staticmethod
    def normalize_records(records: List[Dict]) -> List[Dict]:
        """
        标准化一批字典记录：去除空白字段、统一类型、填充默认值。
        """
        return [
            {
                "id": int(rec.get("id", 0)),
                "name": rec.get("name", "").strip().title(),
                "email": rec.get("email", "").strip().lower(),
                "status": rec.get("status", "active").lower(),
            }
            for rec in records
            if rec.get("name", "").strip()  # 过滤掉空名字的记录
        ]


# 测试
raw_phones = [
    "138-1234-5678", "   ", "15912345678",
    "abc", "18800001111", "123456789", "15912345678",  # 最后这个是重复的
]
print(DataCleaner.clean_phone_numbers(raw_phones))
# ['13812345678', '15912345678', '18800001111']

records = [
    {"id": "1", "name": "  alice WANG  ", "email": "Alice@Example.com"},
    {"id": "2", "name": "", "email": "bob@test.com"},     # 会被过滤
    {"id": "3", "name": "BOB LI", "status": "INACTIVE"},
]
print(DataCleaner.normalize_records(records))
```

---

### 知识点：嵌套推导式

**案例1：二维列表的展平与转置**

```python
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

# 展平（一行）
flat = [x for row in matrix for x in row]
print(flat)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 转置（行变列，列变行）
transposed = [[row[i] for row in matrix] for i in range(3)]
print(transposed)  # [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# 等价的双层 for 循环
transposed_verbose = []
for i in range(3):
    col = []
    for row in matrix:
        col.append(row[i])
    transposed_verbose.append(col)
```

**案例2：条件过滤的组合排列**

```python
# 找出所有两位密码的可能组合
# 第一位: 1-4 的偶数
# 第二位: A-D 中不等于 C 的字母
passwords = [
    f"{num}{char}"
    for num in range(1, 5) if num % 2 == 0    # 外层: 2, 4
    for char in "ABCD" if char != "C"           # 内层: A, B, D
]
print(passwords)
# ['2A', '2B', '2D', '4A', '4B', '4D']

# 等价写法——注意多层推导式中 for 的顺序 = 嵌套 for 的顺序
passwords_verbose = []
for num in range(1, 5):
    if num % 2 == 0:
        for char in "ABCD":
            if char != "C":
                passwords_verbose.append(f"{num}{char}")
```

**案例3：工业级 —— 多层数据结构的字段提取**

```python
from typing import List, Dict, Optional

# 模拟 API 返回的复杂 JSON 结构
api_response = {
    "departments": [
        {
            "name": "技术部",
            "employees": [
                {"name": "张三", "skills": ["Python", "Go", "Docker"]},
                {"name": "李四", "skills": ["Java", "Kubernetes"]},
            ]
        },
        {
            "name": "产品部",
            "employees": [
                {"name": "王五", "skills": ["SQL", "Python"]},
                {"name": "赵六", "skills": []},   # 无技能
            ]
        },
    ]
}

# 用嵌套推导式提取"所有掌握 Python 的员工姓名"
python_devs = [
    emp["name"]
    for dept in api_response["departments"]
    for emp in dept["employees"]
    if "Python" in emp["skills"]
]
print(f"掌握 Python: {python_devs}")  # ['张三', '王五']

# 构建"技能 → 人数"映射
skill_counts = {
    skill: sum(
        1
        for dept in api_response["departments"]
        for emp in dept["employees"]
        if skill in emp["skills"]
    )
    for dept in api_response["departments"]
    for emp in dept["employees"]
    for skill in emp["skills"]
}
print(f"技能统计: {skill_counts}")
# {'Python': 2, 'Go': 1, 'Docker': 1, 'Java': 1, 'Kubernetes': 1, 'SQL': 1}
```

---

## 7.2 字典推导式

**案例1：字典推导式的多种使用方式**

```python
# 从两个列表构建字典
keys = ["name", "age", "city"]
values = ["Alice", 30, "Beijing"]
d1 = {k: v for k, v in zip(keys, values)}
print(d1)  # {'name': 'Alice', 'age': 30, 'city': 'Beijing'}

# 键值对调
d2 = {"a": 1, "b": 2, "c": 3}
swapped = {v: k for k, v in d2.items()}
print(swapped)  # {1: 'a', 2: 'b', 3: 'c'}

# 带过滤条件
scores = {"Alice": 85, "Bob": 92, "Charlie": 78, "David": 60}
passed = {name: score for name, score in scores.items() if score >= 80}
print(passed)  # {'Alice': 85, 'Bob': 92}

# 带变换（修改键或值）
upper_keys = {k.upper(): v for k, v in d2.items()}
print(upper_keys)  # {'A': 1, 'B': 2, 'C': 3}
```

**案例2：嵌套字典的变换**

```python
# 原始数据: 用户ID → 详细信息
users = {
    101: {"name": "Alice", "score": 85, "grade": "B"},
    102: {"name": "Bob", "score": 92, "grade": "A"},
    103: {"name": "Charlie", "score": 78, "grade": "C"},
}

# 提取名字和分数（丢弃其他字段）
simple = {uid: info["name"] for uid, info in users.items()}
print(simple)  # {101: 'Alice', 102: 'Bob', 103: 'Charlie'}

# 只保留分数高于80的用户，并加上"pass"标记
passed = {
    uid: {**info, "status": "PASS"}
    for uid, info in users.items()
    if info["score"] >= 80
}
print(passed[101])  # {'name': 'Alice', 'score': 85, 'grade': 'B', 'status': 'PASS'}
```

**案例3：工业级 —— 配置文件的键名转换**

```python
from typing import Dict, Any

class ConfigTransformer:
    """
    配置转换器。
    将从不同来源（环境变量、JSON配置、命令行）读取的键名统一化。
    常见场景：将不同命名风格统一为 snake_case。
    """

    @staticmethod
    def camel_to_snake(name: str) -> str:
        """驼峰命名 → 蛇形命名: 'dbHost' → 'db_host'"""
        result = []
        for i, char in enumerate(name):
            if char.isupper() and (i > 0 and name[i-1].islower()):
                result.append("_")
            result.append(char.lower())
        return "".join(result)

    @staticmethod
    def normalize_keys(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        递归地将所有键转为 snake_case。
        """
        return {
            ConfigTransformer.camel_to_snake(k): (
                ConfigTransformer.normalize_keys(v)
                if isinstance(v, dict)
                else v
            )
            for k, v in config.items()
        }


# 模拟从某个 Java 系统拿到的配置（驼峰命名）
java_style_config = {
    "dbHost": "localhost",
    "dbPort": 5432,
    "maxPoolSize": 50,
    "connection": {
        "idleTimeout": 30,
        "keepAliveInterval": 5,
    },
}

normalized = ConfigTransformer.normalize_keys(java_style_config)
print(normalized)
# {'db_host': 'localhost', 'db_port': 5432, 'max_pool_size': 50,
#  'connection': {'idle_timeout': 30, 'keep_alive_interval': 5}}
```

---

## 7.3 集合推导式

**案例1：集合推导式的快速去重和改进**

```python
# 传统去重（丢失顺序）
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5]
unique = {x for x in nums}
print(unique)  # {1, 2, 3, 4, 5, 6, 9}

# 提取字段并去重
records = [
    {"role": "admin", "dept": "IT"},
    {"role": "user", "dept": "HR"},
    {"role": "admin", "dept": "IT"},
    {"role": "manager", "dept": "Finance"},
]
roles = {r["role"] for r in records}
print(roles)  # {'admin', 'manager', 'user'}
```

**案例2：集合运算与推导式结合**

```python
# 找出两个文件中都出现的单词
file1_words = {"python", "java", "rust", "go"}
file2_words = {"python", "javascript", "go", "c++"}

# 共同词（交集）
common = {w for w in file1_words if w in file2_words}
print(common)  # {'python', 'go'}
# 更简洁的写法：
common = file1_words & file2_words

# file1 独有的词（差集）
only_file1 = {w for w in file1_words if w not in file2_words}
print(only_file1)  # {'java', 'rust'}
```

**案例3：工业级 —— 用户行为分析的数据预处理**

```python
from typing import List, Dict, Set
from datetime import datetime, timedelta

class UserBehaviorAnalyzer:
    """用户行为分析——集合推导式的数据预处理"""

    @staticmethod
    def get_active_users(
        all_logs: List[Dict],
        days: int = 7,
        min_actions: int = 3
    ) -> Set[str]:
        """
        从日志中找出"活跃用户"：在最近 N 天内至少有 M 次操作的用户。
        集合推导式 + 字典计数 组合使用。
        """
        cutoff = datetime.now() - timedelta(days=days)

        # 统计每个用户的操作次数
        user_counts = {}
        for log in all_logs:
            if log["timestamp"] >= cutoff:
                uid = log["user_id"]
                user_counts[uid] = user_counts.get(uid, 0) + 1

        # 集合推导式：筛选活跃用户
        return {uid for uid, count in user_counts.items() if count >= min_actions}

    @staticmethod
    def find_common_interests(
        user_a_likes: Set[str],
        user_b_likes: Set[str]
    ) -> Dict[str, Set[str]]:
        """
        分析两个用户的兴趣重叠情况。
        返回: {"共同": {...}, "仅A": {...}, "仅B": {...}}
        """
        return {
            "共同": user_a_likes & user_b_likes,
            "仅A": user_a_likes - user_b_likes,
            "仅B": user_b_likes - user_a_likes,
            "合集": user_a_likes | user_b_likes,
        }


# 演示
import random
random.seed(0)

# 模拟日志
logs = [
    {
        "user_id": f"user_{random.randint(1, 5)}",
        "timestamp": datetime.now() - timedelta(hours=random.randint(0, 240)),
    }
    for _ in range(100)
]

active = UserBehaviorAnalyzer.get_active_users(logs, days=5, min_actions=5)
print(f"活跃用户: {active}")

a_likes = {"Python", "Go", "Docker", "Linux", "Vim"}
b_likes = {"Python", "JavaScript", "Docker", "macOS", "VSCode"}
overlap = UserBehaviorAnalyzer.find_common_interests(a_likes, b_likes)
for category, items in overlap.items():
    print(f"{category}: {items}")
```

---

## 7.4 推导式的性能与注意事项

**案例1：速度对比——推导式 vs for 循环**

```python
import timeit

# 推导式通常更快（因为 append 属性查找在 C 层完成）
n = 1_000_000

# for 循环方式
def loop_way():
    res = []
    for i in range(1000):
        if i % 3 == 0:
            res.append(i ** 2)
    return res

# 推导式方式
def comp_way():
    return [i ** 2 for i in range(1000) if i % 3 == 0]

# 在 IPython 中可以用 %timeit:
# %timeit loop_way()  # ≈ 80 µs
# %timeit comp_way()  # ≈ 50 µs  ← 约快 40%
```

**案例2：推导式可读性的边界**

```python
# ✅ 清晰：单层推导式
active_users = [u for u in users if u.is_active]

# ⚠️ 还行：双层 + 简单过滤
user_roles = [role for u in users for role in u.roles if role != "guest"]

# ❌ 太复杂了——应该拆成 for 循环
result = [
    (user.name, project.title)
    for company in companies if company.is_active
    for dept in company.departments if dept.budget > 10000
    for user in dept.users if user.age > 25
    for project in user.projects if project.status == "ongoing"
]
# 这种应该用 for 循环，或者抽成多个中间变量

# 经验法则：超过两层嵌套 → 拆成 for 循环
```

**案例3：工业级 —— 推导式的内存和性能陷阱**

```python
import sys
from typing import List, Iterator

class ComprehensionGuide:
    """
    推导式选择指南：什么时候用哪种推导式。
    """

    @staticmethod
    def compare_memory(n: int = 1_000_000):
        """比较不同推导式的内存占用"""
        # 列表推导式：全部在内存中
        lst = [x ** 2 for x in range(n)]
        print(f"列表推导式: {sys.getsizeof(lst) / 1024 / 1024:.2f} MB")

        # 生成器表达式：几乎不占内存
        gen = (x ** 2 for x in range(n))
        print(f"生成器表达式: {sys.getsizeof(gen)} bytes")

        # 字典推导式
        d = {x: x ** 2 for x in range(n)}
        print(f"字典推导式: {sys.getsizeof(d) / 1024 / 1024:.2f} MB")

    @staticmethod
    def dont_use_comprehension_for_side_effects():
        """
        ❌ 不要用推导式来做有副作用的操作！
        推导式是用来生成新容器的，不是用来替代 for 循环的。
        """
        # ❌ 错误：用推导式打印（滥用）
        # [print(x) for x in range(5)]   # 创建了无用的列表！

        # ✅ 正确：用 for 循环
        for x in range(5):
            print(x)

        # ❌ 错误：用推导式写文件
        # [f.write(line) for line in lines]

        # ✅ 正确：用 for 循环
        # for line in lines:
        #     f.write(line)


ComprehensionGuide.compare_memory(100_000)
# 列表推导式: ~0.8 MB
# 生成器表达式: 120 bytes
# 字典推导式: ~2.9 MB
```

---

## 本章速查

```
┌──────────────────────────────────────────────────────────┐
│  推导式类型        语法                返回类型            │
├──────────────────────────────────────────────────────────┤
│  列表推导式        [x for x in it]      list (立即求值)    │
│  字典推导式        {k:v for k,v in it}  dict (立即求值)    │
│  集合推导式        {x for x in it}      set  (立即求值)    │
│  生成器表达式      (x for x in it)      generator (惰性)   │
└──────────────────────────────────────────────────────────┘

记忆口诀:
  for 后的 if  → 过滤器  → 筛掉不合格的元素
  for 前的 if  → 变换器  → 必须带 else
  方括号装列表，圆括号省内存
  超过两层嵌套就拆成 for 循环
```
