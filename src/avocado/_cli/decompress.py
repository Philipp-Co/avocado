"""CLI for decompressing an avocado-compressed file."""
#
# ---------------------------------------------------------------------------------------------------------------------
#
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

from avocado.avocado import Avocado, create
from avocado.avocado import c as c_backend
from avocado.avocado import python as python_backend
from avocado.exceptions import AvocadoException

#
# ---------------------------------------------------------------------------------------------------------------------
#

def _make_compressor(backend: str) -> Avocado:
    """Create an :class:`Avocado` instance for the requested backend.

    Args:
        backend: One of ``"auto"``, ``"c"`` or ``"python"``.

    Returns:
        Avocado: A compressor instance without codes loaded yet.
    """
    if backend == "c":
        return c_backend()
    if backend == "python":
        return python_backend()
    return create()

#
# ---------------------------------------------------------------------------------------------------------------------
#

def _read_bytes(path: Path) -> bytes:
    """Read the raw bytes of a compressed file.

    Args:
        path: Path to the compressed file to read.

    Returns:
        bytes: The file contents.

    Raises:
        SystemExit: If the file cannot be read.
    """
    try:
        return path.read_bytes()
    except OSError as error:
        raise SystemExit(f"Could not read input file {str(path)!r}: {error}")

#
# ---------------------------------------------------------------------------------------------------------------------
#

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="avocado-decompress",
        description="Decompress an avocado-compressed file back into JSON.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        type=Path,
        help="Compressed file to decompress",
    )
    parser.add_argument(
        "-c",
        "--codes",
        metavar="CODES",
        type=Path,
        required=True,
        help="Codes file created with avocado-codes",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        type=Path,
        default=None,
        help="Target file for the decompressed JSON (default: write to stdout)",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "c", "python"),
        default="auto",
        help="Implementation to use (default: auto)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation for the output (default: 2)",
    )
    return parser

#
# ---------------------------------------------------------------------------------------------------------------------
#

def main(argv: Optional[Sequence[str]] = None) -> int:
    """Decompress a file and write the resulting JSON to a file or stdout.

    Args:
        argv: An optional argument list (defaults to ``sys.argv``); eases testing.

    Returns:
        int: The exit code (0 on success, 1 on a decompression error).
    """
    args = build_parser().parse_args(argv)
    input_path: Path = args.input
    codes_path: Path = args.codes
    output_path: Optional[Path] = args.output
    backend: str = args.backend
    indent: int = args.indent

    compressed = _read_bytes(input_path)

    try:
        compressor = _make_compressor(backend).from_file(codes_path)
        data: Any = compressor.decompress(compressed)
    except FileNotFoundError as error:
        raise SystemExit(f"Could not read codes file {str(codes_path)!r}: {error}")
    except (AvocadoException, AssertionError) as error:
        print(
            f"Failed to decompress (do the codes match the data?): {error}",
            file=sys.stderr,
        )
        return 1

    payload = json.dumps(data, ensure_ascii=False, indent=indent)

    if output_path is not None:
        output_path.write_text(payload, encoding="utf-8")
    else:
        print(payload)

    return 0

#
# ---------------------------------------------------------------------------------------------------------------------
#

if __name__ == "__main__":
    sys.exit(main())
#
# ---------------------------------------------------------------------------------------------------------------------
#
