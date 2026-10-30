#include "read_bytes.h"

#include <fstream>
#include <iterator>
#include <stdexcept>
#include <string>

using namespace std;

vector<char> read_bytes(const char* filename) {
    ifstream input(filename, ios::binary);
    if (!input)
        throw runtime_error(string("Cannot open ") + filename);

    vector<char> bytes{
        istreambuf_iterator<char>(input), istreambuf_iterator<char>()};
    if (input.bad())
        throw runtime_error(string("Cannot read ") + filename);

    return bytes;
}
