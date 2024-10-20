#include <iostream>

class A {
public:
    void hello() {
        std::cout << "Hello A" << std::endl;
    }
};

class B : public virtual A {};

class C : public virtual A {};

class D : public B, public C {};

int main() {
    D d;
    // We can now call single member function hello.
    d.hello();
}