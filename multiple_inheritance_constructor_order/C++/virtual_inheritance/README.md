# Quiz

Which of the following correctly uses virtual inheritance to ensure that class A is instantiated only once when creating an object of class D?

- [ ] 
    ```cpp
    class A { ... };
    class B : public A { ... };
    class C : public virtual A { ... };
    class D : public B, public C { ... };
    ```

- [ ] 
    ```cpp
    class A { ... };
    class B : public virtual A { ... };
    class C : public A { ... };
    class D : public B, public C { ... };
    ```

- [x] 
    ```cpp
    class A { ... };
    class B : public virtual A { ... };
    class C : public virtual A { ... };
    class D : public B, public C { ... };
    ```

- [ ] 
    ```cpp
    class A { ... };
    class B : public A { ... };
    class C : public A { ... };
    class D : public virtual B, public virtual C { ... };
    ```

- [x] 
    ```cpp
    class A { ... };
    class B : public virtual A { ... };
    class C : public virtual A { ... };
    class D : public virtual B, public virtual C { ... };
    ```
