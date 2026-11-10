.DEFAULT_GOAL := all

all: build/peer

build/peer: CMakeLists.txt peer.cpp
	cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
	cmake --build build --target peer -j

clean:
	rm -rf build

.PHONY: all clean
