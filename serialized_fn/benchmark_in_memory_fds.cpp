#include "lib/in_memory_file.h"

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <exception>
#include <fstream>
#include <limits>
#include <memory>
#include <string>
#include <sys/resource.h>
#include <vector>

using namespace std;

bool parse_probed_fd_limit(int argc, char** argv, size_t& probed_fd_limit) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <probed_fd_limit>\n", argv[0]);
        return false;
    }

    char* end = nullptr;
    errno = 0;
    const unsigned long long parsed_limit = strtoull(argv[1], &end, 10);
    if (errno == ERANGE || end == argv[1] || *end != '\0' || argv[1][0] == '-' ||
        parsed_limit == 0 || parsed_limit > numeric_limits<size_t>::max()) {
        fprintf(stderr, "probed_fd_limit must be a positive integer\n");
        return false;
    }
    probed_fd_limit = static_cast<size_t>(parsed_limit);
    return true;
}

int main(int argc, char** argv) {
    size_t probed_fd_limit;
    if (!parse_probed_fd_limit(argc, argv, probed_fd_limit))
        return 2;

    unsigned long long system_limit;
    ifstream system_limit_file("/proc/sys/fs/file-max");
    if (!(system_limit_file >> system_limit)) {
        fprintf(stderr, "cannot read /proc/sys/fs/file-max\n");
        return 1;
    }

    rlimit descriptor_limit{};
    if (getrlimit(RLIMIT_NOFILE, &descriptor_limit) == -1) {
        perror("getrlimit");
        return 1;
    }
    vector<unique_ptr<InMemoryFile>> files;
    files.reserve(probed_fd_limit);

    string stop_reason = "requested probed file limit reached";
    while (files.size() < probed_fd_limit) {
        try {
            files.emplace_back(new InMemoryFile());
        } catch (const exception& error) {
            stop_reason = error.what();
            break;
        }
    }
    printf("%-42s %20llu\n", "System open-file limit (fs.file-max):", system_limit);
    printf("%-42s %20llu\n", "Program open-file limit (RLIMIT_NOFILE):",
           static_cast<unsigned long long>(descriptor_limit.rlim_cur));
    printf("%-42s %20zu\n", "Probed FD limit:", files.size());
    printf("Creation stopped: %s\n", stop_reason.c_str());
    return 0;
}
