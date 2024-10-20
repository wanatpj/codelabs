#include <iostream>

class A {
protected:
    A() { std::cout << "Contruct A." << std::endl; }
};

class B : public A {
protected:
   B() { std::cout << "Contruct B." << std::endl; }
};

class C : public A {
protected:
   C() { std::cout << "Contruct C." << std::endl; }
};

class D : public B, public C {
public:
   D() { std::cout << "Contruct D." << std::endl; }
};

int main() {
    D d;
    return 0;
}