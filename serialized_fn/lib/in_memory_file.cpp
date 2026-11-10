#include "in_memory_file.h"

#include <cerrno>
#include <stdexcept>
#include <string>
#include <system_error>
#include <sys/syscall.h>
#include <unistd.h>

using namespace std;

InMemoryFile::InMemoryFile()
    // Use the syscall because RHEL 7's glibc does not provide the wrapper.
    : fd_(static_cast<int>(syscall(SYS_memfd_create, "circum", 0))) {
    if (fd_ == -1)
        throw system_error(errno, generic_category(), "memfd_create");
}

InMemoryFile::~InMemoryFile() {
    close(fd_);
}

string InMemoryFile::filename() const {
    return "/proc/self/fd/" + to_string(fd_);
}

void InMemoryFile::write_bytes(const vector<char>& bytes) {
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
