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
from abc import ABC, abstractmethod
#
# ---------------------------------------------------------------------------------------------------------------------
#

class Avocado(ABC):
    """A small and hopefully fast Compressor."""

    def __init__(self):
        """Constructor."""
        self.__codes = {}
        pass
    
    def codes(self) -> Dict[str, str]:
        """Get current Codes."""
        return self.__codes.copy()

    def _set_codes(self, codes: Dict[str, str]) -> Self:
        """Set Codes. 

        Child-Classes may override this Function.
        """
        self.__codes = codes
        return self

    def from_file(self, path: Path) -> 'Avocado':
        """Create an Instance."""
        with open(path, mode='r') as file:
            data: str = file.read()
            return self._set_codes(
                loads(data)
            )
    
    @staticmethod
    def generate_codes(schema: Schema) -> Dict[str, str]:
        """Generate Codes from a given Schema."""
        return SchemaCodeGenerator.generate_codes_from_schema(
            schema,
        )

    def from_dict(self, codes: Dict[str, str]) -> Self:
        """Initialize Instance with the given Codes."""
        return self._set_codes(codes)

    def to_file(self, path: str) -> Self:
        """Save the Codes to a File."""
        with open(path, mode='w+') as file:
            file.write(
                dumps(
                    self.codes()
                )
            )
        return self
    
    @abstractmethod
    def compress(self, data: Any) -> bytes:
        """Compress a JSON Serializable Object.

        Args:
            data: A Python Object which is serializable with json.dumps().

        Returns:
            bytes: Returns the compressed Result. 
        """
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> Any:
        """Decompress the given Data.

        Args:
            data: bytes:Compressed Data.

        Returns:
            Any: A Pythonobject which consists of only nativ Python Types such as Dict, List, int, float, bool, str and None.
        """
        pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
