class A:
    def __init__(self):
        print("Construct A.")

class B(A):
    def __init__(self):
        print("Construct B - enter.")
        super(B, self).__init__()
        print("Construct B - exit.")

class C(A):
    def __init__(self):
        print("Construct C - enter.")
        super(C, self).__init__()
        print("Construct C - exit.")

class D(B, C):
    def __init__(self):
        print("Construct D - enter.")
        super(D, self).__init__()
        print("Construct D - exit.")

if __name__ == "__main__":
    d = D()