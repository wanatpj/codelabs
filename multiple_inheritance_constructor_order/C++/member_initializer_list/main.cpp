#include <iostream>

class A {
protected:
    A() { std::cout << "Contruct A." << std::endl; }
};

class B {
protected:
   B() { std::cout << "Contruct B." << std::endl; }
};

class C : public A, public B {
public:
   C() : B(), A() { std::cout << "Contruct C." << std::endl; }
};

int main() {
    C c;
    return 0;
}