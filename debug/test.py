class A:
    def __init__(self, b):
        self.a = b


a = eval("A")(6)
print(a.a)
