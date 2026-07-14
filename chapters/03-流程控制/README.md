# 第三章：程序流程控制

---

## 3.1 条件判断

### 知识点：if / elif / else 与真值测试

**案例1：真值测试——哪些值被判定为 False**

```python
# Python 中以下值在布尔上下文中被视为 False：
falsy_values = [
    False,
    None,
    0,
    0.0,
    "",          # 空字符串
    [],          # 空列表
    {},          # 空字典
    set(),       # 空集合
    (),          # 空元组
    range(0),    # 空 range
]

for val in falsy_values:
    print(f"{repr(val):>15} → {bool(val)}")
# 输出全是 False

# 其余所有值都是 True（包括负数、非空字符串等）
print(bool(-1))        # True
print(bool(" "))       # True （注意：空格不是空字符串！）
print(bool([None]))    # True （包含一个 None 的列表不是空列表）
```

**案例2：链式比较（Python 特有语法）**

```python
age = 25

# ❌ 其他语言常见写法
if age >= 18 and age <= 60:
    print("成年人")

# ✅ Python 链式比较（更简洁，且只求值一次）
if 18 <= age <= 60:
    print("成年人")

# 任意长度的链式比较
a, b, c, d = 1, 2, 3, 4
print(a < b < c < d)     # True
print(a < b > c > d)     # False（b不大于c）

# 等价于：
print(a < b and b < c and c < d)
```

**案例3：工业级——多级条件的状态机**

```python
from enum import Enum
from typing import Dict, Callable, Any

class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"       # 待支付
    PAID = "paid"             # 已支付
    SHIPPED = "shipped"       # 已发货
    DELIVERED = "delivered"   # 已签收
    CANCELLED = "cancelled"   # 已取消
    REFUNDED = "refunded"     # 已退款

class Order:
    """
    订单状态机。用字典映射替代长串 if-elif，
    每种状态只允许特定的合法转换。
    """

    # 状态转换规则表
    _ALLOWED_TRANSITIONS = {
        OrderStatus.PENDING:   [OrderStatus.PAID, OrderStatus.CANCELLED],
        OrderStatus.PAID:      [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED:   [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
        OrderStatus.CANCELLED: [],     # 终态
        OrderStatus.REFUNDED:  [],     # 终态
    }

    def __init__(self, order_id: str):
        self.order_id = order_id
        self.status = OrderStatus.PENDING
        self._history = [self.status]

    def transition_to(self, new_status: OrderStatus) -> bool:
        """尝试转换状态，返回是否成功"""
        allowed = self._ALLOWED_TRANSITIONS.get(self.status, [])

        if new_status not in allowed:
            print(f"❌ 非法转换: {self.status.value} → {new_status.value}")
            print(f"   允许: {[s.value for s in allowed]}")
            return False

        self.status = new_status
        self._history.append(new_status)
        print(f"✅ {self.order_id}: {self._history[-2].value} → {self.status.value}")
        return True

    def get_timeline(self):
        """获取状态时间线"""
        return " → ".join(s.value for s in self._history)


# 使用演示
order = Order("ORD-2024-001")
order.transition_to(OrderStatus.PAID)        # ✅
order.transition_to(OrderStatus.SHIPPED)     # ✅
order.transition_to(OrderStatus.CANCELLED)   # ❌ 非法（已发货不能取消）
order.transition_to(OrderStatus.DELIVERED)   # ✅
print(order.get_timeline())  # pending → paid → shipped → delivered
```

---

### 知识点：match / case 模式匹配（Python 3.10+）

**案例1：基础模式匹配 vs if-elif**

```python
# 传统 if-elif 写法
def handle_event(event):
    if event["type"] == "click":
        return f"点击了 ({event['x']}, {event['y']})"
    elif event["type"] == "keypress":
        return f"按下了 {event['key']}"
    elif event["type"] == "scroll":
        return f"滚动了 {event['delta']} 像素"
    else:
        return "未知事件"

# match-case 写法（更清晰、更安全）
def handle_event_v2(event):
    match event:
        case {"type": "click", "x": x, "y": y}:
            return f"点击了 ({x}, {y})"
        case {"type": "keypress", "key": key}:
            return f"按下了 {key}"
        case {"type": "scroll", "delta": delta}:
            return f"滚动了 {delta} 像素"
        case _:   # 默认匹配
            return "未知事件"

print(handle_event_v2({"type": "click", "x": 100, "y": 200}))  # 点击了 (100, 200)
```

**案例2：序列模式和守卫条件**

```python
# 用 match 解构列表
def analyze_command(cmd):
    match cmd:
        case ["quit"]:
            return "退出程序"
        case ["help"]:
            return "显示帮助"
        case ["add", *items]:               # 匹配 add 后面跟任意数量参数
            return f"添加: {items}"
        case ["move", x, y]:                # 恰好两个参数
            return f"移动到 ({x}, {y})"
        case ["stats", name] if len(name) > 3:  # 守卫条件
            return f"查看 {name} 的统计"
        case _:
            return f"未知命令: {cmd}"

print(analyze_command(["add", "a", "b", "c"]))  # 添加: ('a', 'b', 'c')
print(analyze_command(["move", "10", "20"]))    # 移动到 (10, 20)
print(analyze_command(["stats", "ab"]))          # 未知命令（守卫条件未满足）
```

**案例3：工业级——REST API 路由分发器**

```python
from typing import Any, Dict, Optional

class APIRouter:
    """
    用 match-case 实现的简洁 API 路由。
    适合微服务或 CLI 工具中根据请求类型分发处理。
    """

    def dispatch(self, method: str, path: str, body: Optional[Dict] = None) -> Dict[str, Any]:
        match (method.upper(), path.split("/")):
            # ===== 用户相关 =====
            case ("GET", ["", "api", "users", user_id]):
                return self.get_user(user_id)
            case ("POST", ["", "api", "users"]):
                return self.create_user(body)
            case ("DELETE", ["", "api", "users", user_id]):
                return self.delete_user(user_id)

            # ===== 订单相关 =====
            case ("GET", ["", "api", "orders", order_id]) if order_id.isdigit():
                return self.get_order(int(order_id))
            case ("POST", ["", "api", "orders"]):
                return self.create_order(body)

            # ===== 健康检查 =====
            case ("GET", ["", "health"]):
                return {"status": "ok", "version": "1.0.0"}

            # ===== 默认 =====
            case _:
                return {"error": "Not Found", "status_code": 404}

    # --- 模拟处理方法 ---
    def get_user(self, uid: str):
        return {"action": "get_user", "id": uid}
    def create_user(self, data):
        return {"action": "create_user", "data": data}
    def delete_user(self, uid):
        return {"action": "delete_user", "id": uid}
    def get_order(self, oid: int):
        return {"action": "get_order", "id": oid}
    def create_order(self, data):
        return {"action": "create_order", "data": data}


router = APIRouter()
print(router.dispatch("GET", "/api/users/123"))
# {'action': 'get_user', 'id': '123'}
print(router.dispatch("POST", "/api/users", {"name": "Alice"}))
# {'action': 'create_user', 'data': {'name': 'Alice'}}
print(router.dispatch("GET", "/health"))
# {'status': 'ok', 'version': '1.0.0'}
print(router.dispatch("PUT", "/api/unknown"))
# {'error': 'Not Found', 'status_code': 404}
```

---

## 3.2 循环

### 知识点：while 循环和 while/else

**案例1：while 基础与 break/continue**

```python
# break: 终止整个循环
count = 0
while True:
    count += 1
    print(f"第 {count} 次循环")
    if count >= 5:
        print("达到上限，退出")
        break
# 输出 1 到 5

# continue: 跳过本次迭代的剩余部分
for i in range(10):
    if i % 2 == 0:
        continue   # 跳过偶数
    print(i, end=" ")   # 1 3 5 7 9
```

**案例2：while/else —— 正常退出才执行 else**

```python
# 情况1：正常退出 → else 执行
i = 1
while i <= 3:
    print(i)
    i += 1
else:
    print("循环正常结束")  # 会执行
print("---")

# 情况2：break 退出 → else 不执行
i = 1
while i <= 3:
    print(i)
    if i == 2:
        break
    i += 1
else:
    print("循环正常结束")  # 不会执行
```

**案例3：工业级——带退避策略的重试机制**

```python
import time
import random
import logging
from typing import Callable, Type, Tuple

logger = logging.getLogger(__name__)

def retry_with_backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    指数退避重试装饰器。
    常用于网络请求、数据库操作等不稳定的外部调用。

    退避策略:
        第1次失败等 1s, 第2次等 2s, 第3次等 4s, ...最多等 60s。
        加入随机抖动（jitter），防止"惊群效应"。
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt >= max_attempts:
                        logger.error(f"重试 {max_attempts} 次后仍失败: {e}")
                        break

                    # 计算退避延迟
                    delay = min(base_delay * (backoff_factor ** (attempt - 1)), max_delay)
                    jitter = random.uniform(0, delay * 0.1)  # ±10% 抖动
                    total_delay = delay + jitter

                    logger.warning(
                        f"第 {attempt}/{max_attempts} 次失败: {e}。"
                        f"{total_delay:.1f}s 后重试..."
                    )
                    time.sleep(total_delay)
            else:
                # while/else：理论上不会通过这里（break 退出），但作为防御
                pass

            raise last_exception  # 所有重试都失败

        return wrapper
    return decorator


# 使用演示
@retry_with_backoff(max_attempts=3, base_delay=0.5)
def unstable_network_call():
    """模拟不稳定的网络请求"""
    if random.random() < 0.7:
        raise ConnectionError("网络超时")
    return "请求成功"

# for _ in range(5):
#     try:
#         result = unstable_network_call()
#         print(f"✅ {result}")
#     except ConnectionError:
#         print("❌ 最终失败")
```

---

### 知识点：for 循环的本质

**案例1：for 循环的底层实现**

```python
# for item in iterable:
#     print(item)
#
# 本质上等价于:
iterator = iter([1, 2, 3])
while True:
    try:
        item = next(iterator)
        print(item)
    except StopIteration:
        break
```

**案例2：for/else —— 搜索未找到时执行**

```python
# 经典用法：在列表中搜索
def find_first_even(numbers):
    """找到第一个偶数。找不到时用 else 处理。"""
    for n in numbers:
        if n % 2 == 0:
            print(f"找到了: {n}")
            break         # 找到了 → else 不执行
    else:
        print("没有找到偶数")   # 没 break → else 执行

find_first_even([1, 3, 5, 7])     # 没有找到偶数
find_first_even([1, 3, 4, 7])     # 找到了: 4

# 另一个经典用法：判断质数
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False   # 找到因子
    else:                  # for/else: 完整遍历完所有可能因子
        return True

print(is_prime(17))   # True
print(is_prime(24))   # False
```

**案例3：工业级——批量数据处理的流水线模式**

```python
from typing import Iterator, List, Dict, Any
import time

class BatchProcessor:
    """
    批量数据处理器。
    逐批读取、逐条处理、按批提交——典型的 ETL 流水线模式。
    """

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.total_processed = 0
        self.total_failed = 0
        self._current_batch: List[Dict] = []

    def process_batch(self, batch: List[Dict]) -> List[Dict]:
        """处理一批数据（子类可重写）"""
        results = []
        for item in batch:
            try:
                # 这里是具体的处理逻辑
                item["processed_at"] = time.time()
                item["status"] = "processed"
                results.append(item)
                self.total_processed += 1
            except Exception as e:
                item["status"] = "failed"
                item["error"] = str(e)
                results.append(item)
                self.total_failed += 1
        return results

    def run(self, source: Iterator[Dict]) -> List[Dict]:
        """
        运行流水线。
        逐批读取 → 逐条处理 → 结果汇总。
        """
        all_results = []
        self._current_batch = []

        for item in source:
            self._current_batch.append(item)

            if len(self._current_batch) >= self.batch_size:
                results = self.process_batch(self._current_batch)
                all_results.extend(results)
                self._current_batch = []  # 重置批次
        else:
            # for/else: 处理最后一批不满 batch_size 的数据
            if self._current_batch:
                results = self.process_batch(self._current_batch)
                all_results.extend(results)

        print(f"处理完成: 成功 {self.total_processed}, 失败 {self.total_failed}")
        return all_results


# 使用演示
def data_generator(n: int) -> Iterator[Dict]:
    """模拟数据源"""
    for i in range(n):
        yield {"id": i, "value": f"data_{i}"}

processor = BatchProcessor(batch_size=3)
results = processor.run(data_generator(10))
print(f"共处理 {len(results)} 条")
```

---

## 3.3 可迭代对象与迭代器（入门）

### 知识点：区分可迭代对象和迭代器

**案例1：判断一个对象是不是可迭代/迭代器**

```python
from collections.abc import Iterable, Iterator

# 可迭代对象（Iterable）：能多次遍历
lst = [1, 2, 3]
print(f"list 是 Iterable: {isinstance(lst, Iterable)}")   # True
print(f"list 是 Iterator: {isinstance(lst, Iterator)}")   # False！

# 迭代器（Iterator）：一次性的
it = iter(lst)
print(f"iter(list) 是 Iterable: {isinstance(it, Iterable)}")  # True
print(f"iter(list) 是 Iterator: {isinstance(it, Iterator)}")  # True

# 常见内置类型分类
types_to_check = [
    [], {}, set(), (), "string",         # 可迭代对象
    iter([]), (x for x in range(3)),     # 迭代器
    map(str, [1,2,3]), filter(None, [1,2,3]),  # 迭代器
]

for obj in types_to_check:
    is_it = "✅" if isinstance(obj, Iterator) else "❌"
    print(f"{is_it} Iterator: {type(obj).__name__:>15} → {repr(obj)[:30]}")
```

**案例2：自定义可迭代对象（实现 __iter__）vs 自定义迭代器（实现 __next__）**

```python
class BookShelf:
    """书架：可迭代对象（每次遍历都可以从头开始）"""

    def __init__(self, books):
        self.books = books

    def __iter__(self):
        """返回一个新的迭代器——所以每次遍历都是全新的"""
        return BookIterator(self.books)


class BookIterator:
    """书记员：迭代器（只能往前走，不能后退）"""

    def __init__(self, books):
        self._books = books
        self._index = 0

    def __iter__(self):
        return self    # 迭代器的 __iter__ 返回自身

    def __next__(self):
        if self._index >= len(self._books):
            raise StopIteration
        book = self._books[self._index]
        self._index += 1
        return book


# 可迭代对象可以多次遍历
shelf = BookShelf(["三体", "活着", "百年孤独"])
print("第一遍:", [b for b in shelf])   # ['三体', '活着', '百年孤独']
print("第二遍:", [b for b in shelf])   # ['三体', '活着', '百年孤独']

# 迭代器只能遍历一次
it = BookIterator(["A", "B", "C"])
print("第一遍:", list(it))    # ['A', 'B', 'C']
print("第二遍:", list(it))    # [] — 已耗尽！
```

**案例3：工业级——数据分页迭代器**

```python
from typing import Iterator, List, TypeVar, Generic

T = TypeVar("T")

class PaginatedIterator(Generic[T]):
    """
    分页迭代器。用于 API 分页查询、数据库游标遍历等场景。
    自动处理"加载下一页"的逻辑，使用方只需 for 循环即可。
    """

    def __init__(self, page_fetcher, page_size: int = 100):
        """
        page_fetcher: 可调用对象，签名为 (page_num, page_size) -> List[T]
                      返回空列表表示没有更多数据。
        """
        self._fetcher = page_fetcher
        self._page_size = page_size
        self._page_num = 0
        self._current_page: List[T] = []
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self) -> T:
        # 当前页用完了，加载下一页
        if self._index >= len(self._current_page):
            self._page_num += 1
            self._current_page = self._fetcher(self._page_num, self._page_size)
            self._index = 0
            if not self._current_page:   # 空列表 = 没有更多数据
                raise StopIteration

        item = self._current_page[self._index]
        self._index += 1
        return item


# 模拟数据库分页查询
def mock_db_query(page: int, page_size: int) -> List[dict]:
    """模拟从数据库分批取数据"""
    total = 250
    start = (page - 1) * page_size
    if start >= total:
        return []
    end = min(start + page_size, total)
    return [{"id": i, "name": f"user_{i}"} for i in range(start, end)]


# 使用分页迭代器——使用方完全不需要关心分页逻辑
print("逐条迭代（自动分页）:")
for i, user in enumerate(PaginatedIterator(mock_db_query, page_size=50)):
    print(f"  {user}", end="")
    if (i + 1) % 5 == 0:
        print()
```

---

## 本章速查

| 结构 | 说明 |
|------|------|
| `if/elif/else` | 条件判断，支持链式比较 `0 < x < 10` |
| `match/case` | 模式匹配（3.10+），比 if-elif 更强大 |
| `while` | 条件循环，`while/else` 正常退出执行 else |
| `for` | 迭代循环，`for/else` 未被 break 时执行 else |
| `break` | 终止整个循环 |
| `continue` | 跳过本次迭代 |
| Iterable | 有 `__iter__` 方法，可以多次遍历 |
| Iterator | 有 `__iter__` + `__next__` 方法，一次性 |
