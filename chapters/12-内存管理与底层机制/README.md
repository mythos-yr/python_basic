# 第十二章：内存管理与底层机制

---

## 12.1 引用计数——Python 如何自动回收内存

### 理论：每个对象都有一个"被引用次数"

CPython 主要靠**引用计数**管理内存：每有一个变量指向某个对象，引用计数 +1；变量被删除或重新赋值，引用计数 -1；计数降到 0，对象立即被回收。

**循环引用问题**：如果 A 引用 B，B 也引用 A，它们的计数永远到不了 0——即使外部不再需要它们。这时需要**分代垃圾回收（GC）** 来检测这种循环并回收。

---

### 关键字/语法

| 函数 | 作用 |
|------|------|
| `sys.getrefcount(obj)` | 查看对象的引用计数（结果比实际多1） |
| `id(obj)` | 返回对象的唯一标识（内存地址） |
| `gc.collect()` | 手动触发垃圾回收 |
| `weakref.ref(obj)` | 创建弱引用——不增加引用计数 |

---

### 案例

**案例1：引用计数的增减**

```python
import sys

a = []                        # 引用计数 = 1
print(sys.getrefcount(a) - 1) # 1（减1因为 getrefcount 本身增加临时引用）

b = a                         # +1 → 计数 = 2
print(sys.getrefcount(a) - 1) # 2

del b                         # -1 → 计数 = 1
# 当 del a 后，计数降为 0，对象立即被回收
```

**案例2：循环引用——弱引用来解决**

```python
import weakref

class Node:
    def __init__(self, name):
        self.name = name

# 循环引用（即使 del 外层的 a 和 b，它们的内存不会被立即回收）
a = Node("A")
b = Node("B")
a.ref = b
b.ref = a
del a, b

# 弱引用：不增加引用计数，不影响回收
class NodeGood:
    def __init__(self, name):
        self.name = name
        self._ref = None

    @property
    def ref(self):
        return self._ref() if self._ref else None

    @ref.setter
    def ref(self, node):
        self._ref = weakref.ref(node)  # 不增加引用计数
```

**案例3：小整数缓存——隐藏的内存优化**

```python
# Python 启动时预缓存了 -5 到 256 的整数
a = 256
b = 256
print(a is b)  # True —— 同一个对象（从缓存中取的）

x = 257
y = 257
print(x is y)  # 可能 False！—— 超出缓存范围，分别创建

# ★ 永远用 == 比较值，用 is 只和 None 比较
```

---

## 12.2 可变与不可变——决定"修改"行为的关键

### 理论

| 分类 | 类型 | "修改"的实际行为 |
|------|------|-----------------|
| 不可变 | int, float, str, tuple, frozenset | 创建新对象，变量重新绑定 |
| 可变 | list, dict, set, bytearray | 在原地修改同一对象 |

**这对函数参数传递的影响**：传入可变对象，函数内修改内容会"泄漏"到外部；传入不可变对象，"修改"只是换标签，不影响外部。

---

### 案例

**案例1：`+=` 对不同类型的不同行为**

```python
# 不可变：创建新对象
a = (1, 2, 3)
print(id(a))
a += (4, 5)           # 创建了新元组！
print(id(a))          # id 变了

# 可变：原地修改
b = [1, 2, 3]
print(id(b))
b += [4, 5]           # 等价于 extend，原地修改
print(id(b))          # id 没变！
```

**案例2：函数中"重新赋值" vs "修改内容"**

```python
def reassign(lst):
    lst = [4, 5, 6]    # 只是局部变量换标签，不影响外部

def mutate(lst):
    lst.append(7)      # 修改同一个对象的内容，影响外部

a = [1, 2, 3]
reassign(a)
print(a)  # [1, 2, 3] —— 没变

mutate(a)
print(a)  # [1, 2, 3, 7] —— 变了！
```

**案例3：深浅拷贝——什么时候用哪个**

```python
import copy

original = [1, 2, [10, 20]]

# = 赋值：不是拷贝，是另一张标签
ref = original

# 浅拷贝：外层新列表，内层共享引用
shallow = copy.copy(original)
shallow[2].append(30)     # original[2] 也被修改！

# 深拷贝：递归复制所有层级，完全独立
deep = copy.deepcopy(original)
deep[2].append(40)        # original 完全不受影响
```

---

## 本章速查

| 概念 | 一句话 |
|------|--------|
| 引用计数 | 计数归零→立即回收 |
| 循环引用 | A↔B 互相引用，需 GC 介入 |
| 弱引用 | `weakref`：不增加引用计数 |
| 小整数缓存 | -5 ~ 256 被预缓存复用 |
| `is` vs `==` | is 比身份（id），== 比值 |
| 可变 vs 不可变 | 可变可原地改，不可变只能创建新的 |
| 浅拷贝 vs 深拷贝 | 浅拷贝 = 外层新，内层共享；深拷贝 = 全部独立 |
