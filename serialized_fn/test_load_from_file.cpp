#include "lib/load_circumference.h"

#include <chrono>
#include <cstdio>
#include <exception>

using namespace std;

int main() {
    try {
        const chrono::steady_clock::time_point start = chrono::steady_clock::now();
        CircumferenceLibrary library("./lib/circumference.so");
        const double result = library.circumference(5);
        const double elapsed_us = chrono::duration<double, micro>(
            chrono::steady_clock::now() - start).count();
        printf("%f\n", result);
        printf("Load and call: %.3f us\n", elapsed_us);
    } catch (const exception& error) {
        fprintf(stderr, "%s\n", error.what());
        return 1;
    }
    return 0;
}
