# Shared-library loading tests

Run all commands from `serialized_fn/`.

## Build and run locally

Requires Linux, Make, and a C++11 compiler.

```sh
make test_load_from_file test_load_from_memory
./test_load_from_file
./test_load_from_memory
```

Both tests print `circumference(5)` and the time spent loading the library and
calling the function. The memory test reads the library into a memory-backed
file before timing starts.

```sh
make       # Build lib/circumference.so only
make asm   # Show the library's assembly
make clean # Remove local build outputs
```

## Build and run containers

Podman is the default. To use Docker instead:

```sh
export CONTAINER_ENGINE=docker
```

To switch back:

```sh
export CONTAINER_ENGINE=podman
```

Build and run both tests on UBI 7 and UBI 8:

```sh
make containers-build
make containers-run
```

`containers-run` also builds the images, using cached layers when available.

Build or run a single version and test:

```sh
make container-build RHEL_VERSION=7
make test-file RHEL_VERSION=7
make test-memory RHEL_VERSION=8
```

Both test targets build the image before running. `RHEL_VERSION` defaults to `8`.
