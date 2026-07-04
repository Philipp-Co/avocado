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

from ._native._bindings import _lib, codes_from_dict, Codes_t, AVOCADO_Codec_t
from ctypes import byref, create_string_buffer
from ._avocado_base import Avocado

#
# ---------------------------------------------------------------------------------------------------------------------
#

class AvocadoC(Avocado):
    """A small and hopefully fast Compressor."""

    def __init__(self):
        super().__init__()
        self._codec = None

    def __del__(self):
        if self._codec:
            _lib.AVOCADO_DeInit(byref(self._codec))

    def _set_codes(self, codes: Dict[str, str]) -> Self:
        super()._set_codes(codes)
        if self._codec:
            _lib.AVOCADO_DeInit(byref(self._codec))
        c: Codes_t = codes_from_dict(codes)
        self._codec = AVOCADO_Codec_t(_lib.AVOCADO_Init(byref(c)))
        return self

    def compress(self, data: Any) -> bytes:
        """Compress a JSON Serializable Object.

        Args:
            data: A Python Object which is serializable with json.dumps().

        Returns:
            bytes: Returns the compressed Result. 
        """
        #
        # First 4 Bytes contain the number of Bits which represent the compressed Data.
        #
        minified_string_data: str = dumps(
            data,
            separators=(',',':')
        )
        input_buffer = minified_string_data.encode()
        output_buffer = create_string_buffer(len(input_buffer))
        size = len(output_buffer)
        rc = _lib.AVOCADO_Encode(
             self._codec,
             input_buffer,
             output_buffer,
             size,
        )
        if rc < 0:
            raise AssertionError
        return output_buffer.raw

    def decompress(self, data: bytes) -> Any:
        """Decompress the given Data.

        Args:
            data: bytes:Compressed Data.

        Returns:
            Any: A Pythonobject which consists of only nativ Python Types such as Dict, List, int, float, bool, str and None.
        """
        #
        # First 4 Bytes contain the number of Bits which represent the compressed Data.
        #
        output_buffer = create_string_buffer(4096)
        number_of_bits: int = _lib.AVOCADO_Decode(
            self._codec,
            data,
            output_buffer,
            len(output_buffer)
        )
        return loads(
            bytes(output_buffer[:number_of_bits])
        )

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

