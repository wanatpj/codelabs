.DEFAULT_GOAL := lib/circumference.so

CXXFLAGS ?= -std=c++11
LDFLAGS ?=
CONTAINER_ENGINE ?= podman
RHEL_VERSION ?= 8
IMAGE ?= localhost/serialized-fn:ubi$(RHEL_VERSION)

lib/%.so: lib/%.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -fPIC -shared $< -o $@ $(LDFLAGS)

lib/%.o: lib/%.cpp lib/%.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

test_load_from_file: test_load_from_file.cpp lib/load_circumference.o lib/circumference.so
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< lib/load_circumference.o -o $@ $(LDFLAGS) -ldl

test_load_from_memory: test_load_from_memory.cpp lib/load_circumference.o lib/read_bytes.o lib/circumference.so
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $< lib/load_circumference.o lib/read_bytes.o -o $@ $(LDFLAGS) -ldl

container-build:
	$(CONTAINER_ENGINE) build -f Containerfile --target runtime --build-arg RHEL_VERSION=$(RHEL_VERSION) -t $(IMAGE) .

test-file: container-build
	$(CONTAINER_ENGINE) run --rm $(IMAGE) ./test_load_from_file

test-memory: container-build
	$(CONTAINER_ENGINE) run --rm $(IMAGE) ./test_load_from_memory

containers-build:
	$(MAKE) container-build RHEL_VERSION=7
	$(MAKE) container-build RHEL_VERSION=8

containers-run: containers-build
	$(CONTAINER_ENGINE) run --rm localhost/serialized-fn:ubi7 ./test_load_from_file
	$(CONTAINER_ENGINE) run --rm localhost/serialized-fn:ubi7 ./test_load_from_memory
	$(CONTAINER_ENGINE) run --rm localhost/serialized-fn:ubi8 ./test_load_from_file
	$(CONTAINER_ENGINE) run --rm localhost/serialized-fn:ubi8 ./test_load_from_memory

asm: lib/circumference.so
	objdump -d -C -M intel lib/circumference.so

clean:
	$(RM) lib/*.so lib/*.o test_load_from_file test_load_from_memory

.PHONY: asm clean container-build test-file test-memory containers-build containers-run
