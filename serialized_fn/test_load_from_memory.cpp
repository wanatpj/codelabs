#include "lib/load_circumference.h"
#include "lib/in_memory_file.h"
#include "lib/read_bytes.h"

#include <chrono>
#include <cstdio>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

int main() {
    try {
        const vector<char> bytes = read_bytes("./lib/circumference.so");

        InMemoryFile file;
        file.write_bytes(bytes);
        const string filename = file.filename();
        const chrono::steady_clock::time_point start = chrono::steady_clock::now();
        CircumferenceLibrary library(filename.c_str());
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
