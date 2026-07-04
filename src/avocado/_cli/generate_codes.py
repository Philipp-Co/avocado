"""CLI for generating avocado codes from a Marshmallow schema."""
#
# ---------------------------------------------------------------------------------------------------------------------
#
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Sequence

from marshmallow import Schema

from avocado.avocado import Avocado, create
from avocado.exceptions import AvocadoException

#
# ---------------------------------------------------------------------------------------------------------------------
#

def _load_schema(target: str) -> Schema:
    """Load and instantiate a Marshmallow schema from a ``file.py:SchemaClass`` reference.

    The file path is resolved relative to the current working directory, i.e. the
    location from which the command is invoked.

    Args:
        target: A reference of the form ``path/to/file.py:SchemaClass``.

    Returns:
        Schema: An instantiated schema.

    Raises:
        SystemExit: If the reference is malformed, the file does not exist, cannot
            be imported, or the target is not a Marshmallow schema.
    """
    file_part, separator, attribute = target.rpartition(":")
    if not separator or not file_part or not attribute:
        raise SystemExit(
            "Provide the schema as 'path/to/file.py:SchemaClass', e.g. ./schema.py:UserSchema"
        )

    schema_file = Path(file_part)
    if not schema_file.is_file():
        raise SystemExit(f"Schema file {str(schema_file)!r} does not exist")

    spec = importlib.util.spec_from_file_location(schema_file.stem, schema_file)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load a module from {str(schema_file)!r}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as error:  # noqa: BLE001 - surface any import-time error cleanly
        raise SystemExit(f"Failed to import {str(schema_file)!r}: {error}")

    # getattr is statically typed as Any -> narrow it via isinstance/issubclass
    # so mypy can verify the Schema return type.
    candidate: object = getattr(module, attribute, None)
    if not (isinstance(candidate, type) and issubclass(candidate, Schema)):
        raise SystemExit(f"{attribute!r} in {str(schema_file)!r} is not a Marshmallow schema")

    return candidate()
#
# ---------------------------------------------------------------------------------------------------------------------
#


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="avocado-codes",
        description="Generate avocado codes from a Marshmallow schema.",
    )
    parser.add_argument(
        "schema",
        metavar="FILE:SCHEMA",
        help="Path to a schema file and class, relative to the current directory, "
             "e.g. ./schema.py:UserSchema",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        default=None,
        help="Target file (default: write to stdout)",
    )
    return parser

#
# ---------------------------------------------------------------------------------------------------------------------
#

def main(argv: Optional[Sequence[str]] = None) -> int:
    """Generate codes from a schema and print or save them.

    Args:
        argv: An optional argument list (defaults to ``sys.argv``); eases testing.

    Returns:
        int: The exit code (0 on success, 1 on a code-generation error).
    """
    args = build_parser().parse_args(argv)
    schema_target: str = args.schema
    output_path: Optional[str] = args.output

    schema = _load_schema(schema_target)

    try:
        codes: Dict[str, str] = Avocado.generate_codes(schema)
        if output_path is not None:
            create().from_dict(codes).to_file(output_path)
        else:
            print(json.dumps(codes, ensure_ascii=False, indent=2))
    except AvocadoException as error:
        print(f"Failed to generate codes: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
#
# ---------------------------------------------------------------------------------------------------------------------
#
