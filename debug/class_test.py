class B:

    def __init__(self):
        self.a = [1, 1]


class A(B):
    def add(self):
        self.a[0] += 1


class C(B):
    def add(self):
        self.a[0] += 2


a = A()
c = C()

a.add()
c.add()

print(a.a)
print(c.a)
