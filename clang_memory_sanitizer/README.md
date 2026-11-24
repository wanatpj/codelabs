# MemorySanitizer with Clang

## Requirements

Use Linux with Clang and its MemorySanitizer runtime installed. Check the
Clang resource directory with:

```sh
clang++ -print-resource-dir
```

The directory should contain the MemorySanitizer runtime under `lib/linux/`.
If the build reports that it cannot find `libclang_rt.msan`, install a Clang
package that includes compiler-rt's sanitizer runtimes.

On Ubuntu, install Clang and its runtime with:

```sh
make install-clang
```

## Build and run

Run these commands from this directory:

```sh
make
./uninitialized
./initialized
```

`uninitialized` should report `use-of-uninitialized-value` and exit with a
nonzero status. That failure is expected. `initialized` should exit without a
report.

The Makefile uses these flags:

- `-fsanitize=memory`: instrument the program and link the MemorySanitizer
  runtime.
- `-fsanitize-memory-track-origins=2`: include where the value was created and
  stored in the report.
- `-O1 -g -fno-omit-frame-pointer`: enable optimization and useful stack
  traces.

To use another Clang executable:

```sh
make clean
make CXX=clang++-18
```

If reports do not include source lines, install `llvm-symbolizer` and put it in
`PATH`, or set `MSAN_SYMBOLIZER_PATH` to its path.

## Limitations

MemorySanitizer requires instrumented program code. Uninstrumented libraries
can hide uninitialized data or cause misleading reports. The runtime intercepts
many common C library calls, but third-party libraries may need to be rebuilt
with MemorySanitizer. Do not use the sanitizer runtime in production binaries.

MemorySanitizer uses extra memory and virtual address space. Static linking is
not supported.

See the [Clang MemorySanitizer documentation](https://clang.llvm.org/docs/MemorySanitizer.html)
for details.

## Clean

```sh
make clean
```
