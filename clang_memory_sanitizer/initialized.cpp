#include <cstdio>

int main() {
    int* values = new int[2];
    values[0] = 0;
    values[1] = 0;

    volatile int value = values[1];
    if (value)
        std::puts("nonzero");

    delete[] values;
}
