"""Main Class."""
#
# ---------------------------------------------------------------------------------------------------------------------
#
from typing import Dict, Any, Tuple, Set
from math import ceil
from json import dumps, loads
from ._huffman.huffman_tree import Tree, HuffmanTreeIterator, TreeBuilder, generate_huffman_codes
from ._huffman.generate_codes import _build_huffman_tree
from .exceptions import AvocadoStringFoundException
from dataclasses import dataclass
from marshmallow import Schema, fields, validate 
from marshmallow.fields import Field
from ._substitute.marshmallow_substitution import MarshmallowSubstitutor
from ._huffman.codes_from_schema import SchemaCodeGenerator
from pathlib import Path

from ._native._bindings import _lib, codes_from_dict, Codes_t
from ctypes import byref, create_string_buffer
from ._avocado_base import Avocado

#
# ---------------------------------------------------------------------------------------------------------------------
#

class AvocadoPy(Avocado):
    """A small and hopefully fast Compressor."""

    def __init__(self) -> None:
        super().__init__()
        pass

    def compress(self, data: Any) -> bytes:
        #
        # First 4 Bytes contain the number of Bits which represent the compressed Data.
        #
        codes = self.codes()
        minified_string_data: str = dumps(
            data,
            separators=(',',':')
        )
        number_of_bits: int = 0
        i: int = 0
        code: str = ''
        while i < len(minified_string_data):
            code = codes[minified_string_data[i]]
            number_of_bits += len(code)
            i += 1

        output: List[int] = [0 for _ in range(ceil(number_of_bits / 8))]
        current_bit: int = 0
        i = 0
        while i < len(minified_string_data):
            code: str = codes[minified_string_data[i]]
            j: int = 0
            while j < len(code):
                byte: int = (current_bit + j) // 8
                bit: int = (current_bit + j) % 8
                output[byte] = output[byte] | ((1 if code[j] == '1' else 0) << bit)
                j += 1
            current_bit += j
            i += 1
        return bytes(
            [number_of_bits & 0xFF, (number_of_bits >> 8) & 0xFF, (number_of_bits >> 16) & 0xFF, (number_of_bits >> 24) & 0xFF] + output
        )

    def decompress(self, data: bytes) -> Any:
        #
        # First 4 Bytes contain the number of Bits which represent the compressed Data.
        #
        number_of_bits: int = int(data[0]) | (int(data[1]) << 8) | (int(data[2]) << 16) | (int(data[3]) << 24)
        data = data[4:]
        data_as_int: List[int] = [int(x) for x in data]
        t: Tree = TreeBuilder.from_dict(
            self.codes()
        )
        decoded_string_data: str = ''
        it: HuffmanTreeIterator = t.iterator()
        i: int = 0
        while i < number_of_bits:
            try:
                byte: int = i // 8
                bit: int = i % 8
                if it.next_bit(
                    bool(data_as_int[byte] & (1 << bit))
                ):
                    decoded_string_data += it.symbol() 
                    it = t.iterator()
            except AssertionError as e:
                raise AssertionError from e
            i += 1
        return loads(
            decoded_string_data,
        )

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

