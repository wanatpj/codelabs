CXX = clang++
CXXFLAGS ?= -std=c++17 -O1 -g -fsanitize=memory -fsanitize-memory-track-origins=2 -fno-omit-frame-pointer -fno-optimize-sibling-calls

all: uninitialized initialized

install-clang:
	sudo apt-get update
	sudo apt-get install -y clang libclang-rt-dev

uninitialized: uninitialized.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

initialized: initialized.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@

clean:
	$(RM) uninitialized initialized

.PHONY: all clean install-clang
