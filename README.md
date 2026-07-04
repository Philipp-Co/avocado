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
