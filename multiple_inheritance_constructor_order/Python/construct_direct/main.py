class A:
    def __init__(self):
        print("Construct A.")

class B(A):
    def __init__(self):
        print("Construct B - enter.")
        A.__init__(self)
        print("Construct B - exit.")

class C(A):
    def __init__(self):
        print("Construct C - enter.")
        A.__init__(self)
        print("Construct C - exit.")

class D(B, C):
    def __init__(self):
        print("Construct D - enter.")
        B.__init__(self)
        C.__init__(self)
        print("Construct D - exit.")

if __name__ == "__main__":
    d = D()