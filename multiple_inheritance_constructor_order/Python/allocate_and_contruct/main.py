class A:
    def __new__(cls):
        print("Allocate A.")
        return super().__new__(cls)

    def __init__(self):
        print("Construct A.")

class B(A):
    def __new__(cls):
        print("Allocate B - enter.")
        result = super().__new__(cls)
        print("Allocate B - exit.")
        return result

    def __init__(self):
        print("Construct B - enter.")
        super().__init__()
        print("Construct B - exit.")

class C(A):
    def __new__(cls):
        print("Allocate C - enter.")
        result = super().__new__(cls)
        print("Allocate C - exit.")
        return result

    def __init__(self):
        print("Construct C - enter.")
        super().__init__()
        print("Construct C - exit.")

class D(B, C):
    def __new__(cls):
        print("Allocate D - enter.")
        result = super().__new__(cls)
        print("Allocate D - exit.")
        return result

    def __init__(self):
        print("Construct D - enter.")
        super().__init__()
        print("Construct D - exit.")

if __name__ == "__main__":
    d = D()

    print(D.mro())