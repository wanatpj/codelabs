#pragma once

#include <string>
#include <vector>

class InMemoryFile {
public:
    InMemoryFile();
    ~InMemoryFile();

    InMemoryFile(const InMemoryFile&) = delete;
    InMemoryFile& operator=(const InMemoryFile&) = delete;

    std::string filename() const;
    void write_bytes(const std::vector<char>& bytes);

private:
    int fd_;
};
