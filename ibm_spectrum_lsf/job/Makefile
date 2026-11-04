.DEFAULT_GOAL := build/monte_carlo

CXXFLAGS ?= -std=c++11 -O2 -Wall -Wextra -pedantic

build/monte_carlo: monte_carlo.cpp
	mkdir -p build
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< -o $@ $(LDFLAGS)

clean:
	$(RM) build/monte_carlo

.PHONY: clean
