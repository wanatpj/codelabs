#include "lib/load_circumference.h"
#include "lib/read_bytes.h"

#include <cerrno>
#include <chrono>
#include <cstdio>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>
#include <sys/syscall.h>
#include <unistd.h>

using namespace std;

class MemoryFile {
public:
    // RHEL 7's glibc has no memfd_create wrapper; call the kernel directly.
    MemoryFile() : fd_(static_cast<int>(syscall(SYS_memfd_create, "circum", 0))) {
        if (fd_ == -1)
            throw system_error(errno, generic_category(), "memfd_create");
    }

    ~MemoryFile() { close(fd_); }

    MemoryFile(const MemoryFile&) = delete;
    MemoryFile& operator=(const MemoryFile&) = delete;

    string filename() const {
        return "/proc/self/fd/" + to_string(fd_);
    }

    void write_bytes(const vector<char>& bytes) {
        size_t offset = 0;
        while (offset < bytes.size()) {
            const ssize_t count = write(fd_, bytes.data() + offset, bytes.size() - offset);
            if (count == -1) {
                if (errno == EINTR)
                    continue;
                throw system_error(errno, generic_category(), "write");
            }
            if (count == 0)
                throw runtime_error("write: no progress");
            offset += static_cast<size_t>(count);
        }
    }

private:
    int fd_;
};

int main() {
    try {
        const vector<char> bytes = read_bytes("./lib/circumference.so");

        MemoryFile file;
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
