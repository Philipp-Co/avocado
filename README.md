# avocado

A small library for compressing JSON objects.

`avocado` builds Huffman codes from a schema and uses them to compress and decompress
JSON data whose shape is known in advance. Because the codes are derived from the
schema, the compressed payload does not need to carry a dictionary with it — the same
codes are used on both ends.

It ships two interchangeable backends behind a single interface:

- a pure **Python** implementation, and
- a **C** implementation loaded via `ctypes` (falls back to Python when the native
  library is not available).

## Installation

```bash
pip install -e .
```

This also registers the command-line tools described below.

## Building the package

`avocado` combines a Python package with a native C library (`libavocado`). The
native library must be built **before** the Python package is installed or built,
since `ctypes` loads it from a fixed path inside the package
(`src/avocado/_native/lib/`).

### 1. Build the native library

```bash
cmake -S native -B native/build
cmake --build native/build
```

This compiles `native/src/*.c` and places the result
(`libavocado.dylib` / `libavocado.so` / `avocado.dll`, depending on the platform)
directly into `src/avocado/_native/lib/`, where the Python bindings expect it.

### 2. Build/install the Python package

For local development, an editable install picks up the native library directly
from the source tree:

```bash
pip install -e .
```

To build a distributable wheel/sdist instead:

```bash
python -m build
```

The native library is declared as package data (see `[tool.setuptools.package-data]`
in `pyproject.toml`), so `libavocado.*` is bundled into wheels built this way as
well — as long as it already exists under `src/avocado/_native/lib/` when step 2
runs. Rebuild step 1 first if you change any file under `native/`.

> **Note:** the resulting wheel is still tagged as pure-Python
> (`py3-none-any`), even though it contains a platform-specific binary. It works
> for local use, but is not safe to publish as-is for distribution across
> platforms — that would require building it as a proper platform wheel (e.g.
> via a build backend that compiles the native library as part of the build,
> such as `scikit-build-core` or a `setuptools.Extension`).

## Command-line usage

Three commands cover the full round-trip. They are meant to be used in sequence:
first generate codes from a schema, then compress, then decompress.

Assume a file `schema.py` in the current directory that defines a schema class
`Test`, together with some data to compress:

```json
// data.json
{"int_field": 1235}
```

### 1. Generate codes

The schema is referenced as `FILE:SCHEMA`, where `FILE` is a path **relative to the
current directory** and `SCHEMA` is the schema class name.

```bash
avocado-codes ./schema.py:Test -o codes.json
```

Without `-o`, the codes are printed to stdout.

### 2. Compress

```bash
avocado-compress data.json -c codes.json -o data.avo
```

### 3. Decompress

```bash
avocado-decompress data.avo -c codes.json -o restored.json
```

`restored.json` now contains the original data again.

### Command reference

| Command | Purpose | Key options |
| --- | --- | --- |
| `avocado-codes FILE:SCHEMA` | Generate codes from a schema | `-o/--output` |
| `avocado-compress INPUT` | Compress a JSON file | `-c/--codes` (required), `-o/--output`, `--backend` |
| `avocado-decompress INPUT` | Decompress back to JSON | `-c/--codes` (required), `-o/--output`, `--backend`, `--indent` |

`--backend` accepts `auto` (default), `c` or `python`. Use `--help` on any command
for the full list of options.

> **Note:** compression and decompression must use the *same* codes. The codes must
> also cover every character that appears in the data; codes generated from a schema
> that does not match the data will fail.

## Library usage

The public API lives in `avocado.avocado`.

```python
from avocado.avocado import Avocado, create

from schema import Test

# 1. Generate codes from a schema.
codes = Avocado.generate_codes(Test())

# 2. Create a compressor and load the codes.
compressor = create().from_dict(codes)     # or python() / c()

# 3. Round-trip.
data = {"int_field": 1235}
compressed = compressor.compress(data)     # -> bytes
restored = compressor.decompress(compressed)

assert restored == data
```

### Choosing a backend

```python
from avocado.avocado import create, python, c

compressor = create()    # C if available, otherwise Python
compressor = python()    # force the pure-Python backend
compressor = c()         # force the C backend
```

### Persisting codes

```python
compressor.to_file("codes.json")           # save the current codes
compressor = create().from_file("codes.json")  # load them again
```

## License

MIT
