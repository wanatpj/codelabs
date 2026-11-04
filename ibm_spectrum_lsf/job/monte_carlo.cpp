#include <cstdint>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>

using namespace std;

uint64_t parse_unsigned(const string& text) {
    if (text.empty() || text.find_first_not_of("0123456789") != string::npos)
        throw invalid_argument("Expected an unsigned integer");
    size_t consumed = 0;
    const uint64_t value = stoull(text, &consumed);
    if (consumed != text.size())
        throw invalid_argument("Invalid integer");
    return value;
}

int main(int argc, char** argv) {
    try {
        if (argc != 3)
            throw invalid_argument("Usage: monte_carlo SAMPLES SEED");
        const uint64_t samples = parse_unsigned(argv[1]);
        const uint64_t seed = parse_unsigned(argv[2]);
        if (samples == 0)
            throw invalid_argument("SAMPLES must be positive");

        mt19937_64 random(seed);
        uint64_t hits = 0;
        for (uint64_t i = 0; i < samples; ++i) {
            // Explicit conversion avoids library-specific uniform distributions.
            const double x = (random() >> 11) * (1.0 / 9007199254740992.0);
            const double y = (random() >> 11) * (1.0 / 9007199254740992.0);
            hits += x * x + y * y <= 1.0;
        }
        cout << "{\"samples\":" << samples << ",\"seed\":" << seed
             << ",\"hits\":" << hits << "}\n";
    } catch (const exception& error) {
        cerr << error.what() << '\n';
        return 1;
    }
}
