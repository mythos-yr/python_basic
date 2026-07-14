# 测试生成器

def get_el():
    yield "hello"
    yield "world"


g = get_el()
print(next(g))
print(next(g))


# 异常
# print(next(g))

# 累加器——收一个值，累加，返回当前总和

def accumulator():
    total = 0
    while True:
        received = yield total
        if received is None:
            break
        total += received


g = accumulator()
next(g)
print(g.send(19))
print(g.send(None))
print(g.send(19))
g.close()