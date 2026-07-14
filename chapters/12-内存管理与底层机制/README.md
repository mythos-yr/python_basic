# 第十二章：内存管理与底层机制

---

## 12.1 引用计数——Python 如何自动回收内存

### 理论：每个对象都有一个"被引用的次数"

每有一个变量指向某对象，引用计数 +1；变量删除或重新赋值，计数 -1；**计数降到 0 → 对象立即被回收**（CPython 的机制）。

**循环引用问题**：A 引用 B，B 也引用 A → 即使外部不再需要它们，引用计数永远到不了 0。这时需要**分代 GC**（garbage collector）检测并回收循环引用。

---

### 关键字/函数

| 函数 | 作用 |
|------|------|
| `sys.getrefcount(obj)` | 查看引用计数（结果比实际多 1——函数形参是临时引用） |
| `id(obj)` | 返回对象唯一标识（CPython 中是内存地址） |
| `gc.collect()` | 手动触发分代垃圾回收 |
| `gc.get_objects()` | 获取所有被 GC 追踪的对象 |
| `weakref.ref(obj)` | 创建弱引用——**不增加引用计数** |
| `del x` | 删除变量引用（引用计数 -1） |

**内置优化**：
- **小整数缓存池**：-5 ~ 256 的 int 对象在 Python 启动时预创建，所有引用复用同一对象
- **字符串驻留 (interning)**：短字符串和标识符可能被自动 intern，共享同一对象

---

### 案例

**案例1：引用计数的增减和对象回收**

```python
import sys

a = []                           # 计数 = 1
print(sys.getrefcount(a))        # 2（getrefcount 本身增加临时引用）

b = a                            # 计数 = 2
del b                            # 计数 = 1
# del a                          # 计数 = 0 → 对象被回收
```

**案例2：小整数缓存——`is` 的行为会变化**

```python
a = 256; b = 256
print(a is b)   # True  —— 在缓存池中，同一个对象

x = 257; y = 257
print(x is y)   # 可能是 False —— 超出缓存范围，分别创建

# ★ 永远用 == 比较值，用 is 只比较 None
```

**案例3：弱引用——不阻止对象被回收**

```python
import weakref

class Node:
    def __init__(self, name): self.name = name

# 普通引用 → 循环引用问题
a = Node("A"); b = Node("B")
a.ref = b; b.ref = a
del a; del b           # 循环引用需要 GC 介入才回收

# 弱引用 → 不增加引用计数，不影响回收
class NodeSafe:
    def __init__(self, name): self.name = name; self._ref = None
    @property
    def ref(self):
        return self._ref() if self._ref else None
    @ref.setter
    def ref(self, node):
        self._ref = weakref.ref(node)
```

**案例4（工业级）：内存泄漏排查工具**

```python
import gc
from collections import Counter

# 按类型统计当前内存中的活跃对象数量
counts = Counter(type(obj).__name__ for obj in gc.get_objects())
for name, cnt in counts.most_common(10):
    print(f"{name:>25}: {cnt:>8}")
```

---

## 12.2 可变与不可变

### 理论

| 分类 | 类型 | "修改"时的实际行为 |
|------|------|-------------------|
| **不可变** | int, float, str, tuple, frozenset | **创建新对象**，变量重新绑定 |
| **可变** | list, dict, set, bytearray | **原地修改**，同一对象 |

**对函数参数传递的影响**：传入可变对象 → 函数内修改内容会"泄漏"到外部；传入不可变对象 → 函数内的"修改"只是让局部变量指向新对象，不影响外部。

---

### 案例

**案例1：`+=` 对不同类型的行为不同**

```python
# 不可变：创建新对象
a = (1, 2, 3); id_before = id(a)
a += (4, 5)
print(id(a) == id_before)  # False —— 新元组

# 可变：原地修改
b = [1, 2, 3]; id_before = id(b)
b += [4, 5]
print(id(b) == id_before)  # True —— 同一列表
```

**案例2：函数内"重新赋值" vs "修改内容"**

```python
def reassign(lst):
    lst = [4, 5, 6]     # 只是局部变量换标签

def mutate(lst):
    lst.append(7)       # 修改原对象

a = [1, 2, 3]; reassign(a); print(a)  # [1, 2, 3] ——没变
a = [1, 2, 3]; mutate(a); print(a)    # [1, 2, 3, 7] ——变了
```

**案例3：深浅拷贝——何时用哪个**

| 方式 | 效果 |
|------|------|
| `b = a` | 不拷贝，多贴标签 |
| `b = a.copy()` / `a[:]` | **浅拷贝**：外层新，内层共享引用 |
| `b = copy.deepcopy(a)` | **深拷贝**：递归复制，完全独立 |

```python
import copy
original = [1, 2, [10, 20]]
shallow = copy.copy(original)
deep = copy.deepcopy(original)

original[2].append(30)
print(shallow[2])  # [10, 20, 30] —— 受影响（共享内层）
print(deep[2])     # [10, 20]     —— 不受影响（完全独立）
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| 引用计数 | 归零 → 立即回收 |
| 循环引用 | A↔B 互相引用，需 GC 扫描 |
| 弱引用 | `weakref`：不增加引用计数 |
| 小整数缓存 | -5~256 预创建，共享复用 |
| 字符串驻留 | 短字符串可能自动 intern |
| `is` vs `==` | is 比身份，== 比值 |
| 可变 vs 不可变 | 可变原地改，不可变创建新的 |
| 浅拷贝 vs 深拷贝 | 浅=外层新内层共享，深=完全独立 |
