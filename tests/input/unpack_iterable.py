def f1():
    return 5

a = 1
b = [2,3]
c = [a, *b, 4, f1(), *(6,), (7,), *{8}, {9}, *[10], [11]]
print(c)