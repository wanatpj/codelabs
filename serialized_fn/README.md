# Shared-library loading

Run these commands from `serialized_fn/`. Requirements: Linux, Make, and a
C++11 compiler.

## Run locally

Build both programs:

```sh
make test_load_from_file test_load_from_memory
```

Run them:

```sh
./test_load_from_file
./test_load_from_memory
```

Each program calls `circumference(5)` and prints the result and elapsed time.
The memory test copies the shared library into a Linux memfd, then loads it.

Other commands:

```sh
make       # Build lib/circumference.so
make asm   # Print the shared library's assembly
make clean # Remove generated files
```

## Run in UBI 7 and UBI 8

Podman is the default container engine. `containers-run` builds both images and
runs both programs in each image:

```sh
make containers-run
```

Build the images without running the programs:

```sh
make containers-build
```

Use Docker instead of Podman:

```sh
CONTAINER_ENGINE=docker make containers-run
```

## Benchmark memfd limits

Run the benchmark in both images:

```sh
make containers-benchmark
```

The benchmark requests up to 2,000,000 memfds. It does not change system or
process limits. It prints the system-wide `fs.file-max`, the process
`RLIMIT_NOFILE`, the number of memfds it created, and the reason it stopped.

Run it in one image:

```sh
make benchmark-memory-fds RHEL_VERSION=7
```

Results:
```
podman run --rm localhost/serialized-fn:ubi7 ./benchmark_in_memory_fds 2000000
System open-file limit (fs.file-max):       9223372036854775807
Program open-file limit (RLIMIT_NOFILE):                1048576
Probed FD limit:                                        1048572
Creation stopped: memfd_create: Too many open files
podman run --rm localhost/serialized-fn:ubi8 ./benchmark_in_memory_fds 2000000
System open-file limit (fs.file-max):       9223372036854775807
Program open-file limit (RLIMIT_NOFILE):                1048576
Probed FD limit:                                        1048572
Creation stopped: memfd_create: Too many open files
```
