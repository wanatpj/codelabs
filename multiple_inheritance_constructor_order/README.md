# Constructor Execution Flow within Multiple Inheritance

What is multiple inheritance. Explore below:
- `multiple_inheritance_constructor_order/C++/multiple_inheritance`

Multiple inheritance causes several problems like:
- diamond problem
- complexity in method resolution
- constructor resolution order
, therefore a few programming languages resigned from supporting this feature.

Here, we are going to take a look a few programming languages that supports multiple inheritance.
In our case, we will consider C++ and Python.

Python and C++ are two different cases when it comes to determining the order of base classes execution.
In C++, you can, but you don't have to define how `call to the base class` looks like.
In Python, it is required. If you don't call super constructor then it won't be called.

## C++

Please consider examples in the following order:
- `multiple_inheritance_constructor_order/C++/non_virtual_inheritance`
- `multiple_inheritance_constructor_order/C++/virtual_inheritance`
- `multiple_inheritance_constructor_order/C++/member_initializer_list`

You can find that constructors are called:
- depth first, left to right traversal of base-specifier list
- when we deal with virtual inheritance then class will be initialized only once
- order of base class initializatrion in member initializer list does **not** matter

## Python

Please consider examples in the following order:
- `multiple_inheritance_constructor_order/Python/construct`
- `multiple_inheritance_constructor_order/Python/method`
- `multiple_inheritance_constructor_order/Python/construct_legacy_style`

Python is using MRO (Method Resolution Order) to determine in which order methods (e.g constructors) should be called.

Compare `Python/construct` and `Python/method` to see that the execution order is the same.

It is possible to call base class constructors in a different order than the lineralization order from MRO.
One can call the constructors directly. See:
- `multiple_inheritance_constructor_order/Python/construct_direct`

Allocation of Python class executes in the MRO order, but before the constructor.
- `multiple_inheritance_constructor_order/Python/allocate_and_contruct`

# Summary
- C++ inheritance structure is more like a graph, while for Python is linear
- Python handles calling of base class constructor via explict invocation in the constructor body
while C++ does not support that and requires custom calling convetion of base class to be defined
in member initilizer list
- In Python, even when you call a super constructor, instead of calling the base, it can call sibling or any other
class that is next in linearization of the class that is instantiated
- Calling python base class constructor directly (`multiple_inheritance_constructor_order/Python/construct_direct`)
can immitate behavior of C++ non-virtual inheritance