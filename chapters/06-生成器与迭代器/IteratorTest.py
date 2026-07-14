from collections.abc import Iterator, Iterable

# 可迭代对象不一定是迭代器,迭代器一定是可迭代对象
# 迭代器实现了迭代器协议
ls = [2, 3]
it = iter(ls)
print(isinstance(ls, Iterable))
print(isinstance(ls, Iterator))
print(isinstance(it, Iterator))
print(isinstance(it, Iterable))


# 自定义一个迭代器实现计数器,当计数器为0的时候自动结束

class CountDown:
    def __init__(self, countNumber):
        self.countNumber = countNumber

    # 实现迭代器协议
    def __iter__(self):
        return self

    def __next__(self):
        if self.countNumber < 0:
            raise StopIteration
        value = self.countNumber
        self.countNumber -=1
        return value



print(list(CountDown(15)))