#include <iostream>

class A {
public:
    void hello() {
        std::cout << "Hello A" << std::endl;
    }
};

class B : public A {};

class C : public A {};

class D : public B, public C {};

int main() {
    D d;
    d.B::hello();
    d.C::hello();
    // d.hello();  // Compile Error: request for member ‘hello’ is ambiguous
}