class A:
    def fn(self):
        print("fn A.")

class B(A):
    def fn(self):
        print("fn B - enter.")
        super().fn()
        print("fn B - exit.")

class C(A):
    def fn(self):
        print("fn C - enter.")
        super().fn()
        print("fn C - exit.")

class D(B, C):
    def fn(self):
        print("fn D - enter.")
        super().fn()
        print("fn D - exit.")

if __name__ == "__main__":
    D().fn()