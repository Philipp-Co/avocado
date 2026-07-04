"""CLI for compressing a JSON file with avocado."""
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

def _read_json(path: Path) -> Any:
    """Read and parse a JSON file into a Python object.

    Args:
        path: Path to the JSON file to read.

    Returns:
        Any: The parsed Python object.

    Raises:
        SystemExit: If the file is missing or contains invalid JSON.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise SystemExit(f"Could not read input file {str(path)!r}: {error}")

    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Input file {str(path)!r} is not valid JSON: {error}")

#
# ---------------------------------------------------------------------------------------------------------------------
#

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="avocado-compress",
        description="Compress a JSON file using previously generated avocado codes.",
    )
    parser.add_argument(
        "input",
        metavar="INPUT",
        type=Path,
        help="JSON file to compress",
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
        help="Target file for the compressed bytes (default: write to stdout)",
    )
    parser.add_argument(
        "--backend",
        choices=("auto", "c", "python"),
        default="auto",
        help="Implementation to use (default: auto)",
    )
    return parser

#
# ---------------------------------------------------------------------------------------------------------------------
#

def main(argv: Optional[Sequence[str]] = None) -> int:
    """Compress a JSON file and write the result to a file or stdout.

    Args:
        argv: An optional argument list (defaults to ``sys.argv``); eases testing.

    Returns:
        int: The exit code (0 on success, 1 on a compression error).
    """
    args = build_parser().parse_args(argv)
    input_path: Path = args.input
    codes_path: Path = args.codes
    output_path: Optional[Path] = args.output
    backend: str = args.backend

    data = _read_json(input_path)

    try:
        compressor = _make_compressor(backend).from_file(codes_path)
        compressed: bytes = compressor.compress(data)
    except FileNotFoundError as error:
        raise SystemExit(f"Could not read codes file {str(codes_path)!r}: {error}")
    except KeyError as error:
        print(
            f"Input contains a character without a matching code: {error}",
            file=sys.stderr,
        )
        return 1
    except AvocadoException as error:
        print(f"Failed to compress: {error}", file=sys.stderr)
        return 1

    if output_path is not None:
        output_path.write_bytes(compressed)
    else:
        sys.stdout.buffer.write(compressed)

    return 0

#
# ---------------------------------------------------------------------------------------------------------------------
#

if __name__ == "__main__":
    sys.exit(main())
#
# ---------------------------------------------------------------------------------------------------------------------
#
