"""Regression tests for the off-by-one bug affecting 1-bit Huffman codes."""
#
# ---------------------------------------------------------------------------------------------------------------------
#
from typing import Dict, Any
from unittest import TestCase
from ctypes import byref, create_string_buffer, Array, c_char
from avocado.avocado import c, python, Avocado
from avocado._native._bindings import _lib, codes_from_dict, AVOCADO_Codec_t, Codes_t
#
# ---------------------------------------------------------------------------------------------------------------------
#

CODES_WITH_SINGLE_BIT_CODE: Dict[str, str] = {
    '"': '0',
    'a': '100',
    'b': '101',
    'c': '110',
    'd': '111',
}

#
# ---------------------------------------------------------------------------------------------------------------------
#

class TestHuffmanSingleBitCodes(TestCase):
    """Covers the 1-bit-code case on both the native (C) and the Python level."""

    def test_native_encode_decode_round_trip(self) -> None:
        """AVOCADO_Encode/AVOCADO_Decode must round-trip data through a 1-bit code."""
        codes: Codes_t = codes_from_dict(CODES_WITH_SINGLE_BIT_CODE)
        codec: AVOCADO_Codec_t = AVOCADO_Codec_t(_lib.AVOCADO_Init(byref(codes)))

        input_bytes: bytes = b'"abacabad"'
        output_buffer: Array[c_char] = create_string_buffer(len(input_bytes) + 10)
        number_of_bits: int = _lib.AVOCADO_Encode(
            codec, input_bytes, output_buffer, len(output_buffer)
        )
        self.assertGreater(number_of_bits, 0)

        decode_buffer: Array[c_char] = create_string_buffer(4096)
        number_of_characters: int = _lib.AVOCADO_Decode(
            codec, output_buffer.raw, decode_buffer, len(decode_buffer)
        )

        self.assertEqual(number_of_characters, len(input_bytes))
        self.assertEqual(decode_buffer.raw[:number_of_characters], input_bytes)

        _lib.AVOCADO_DeInit(byref(codec))

    def test_avocado_c_round_trip_with_single_bit_code(self) -> None:
        """The full AvocadoC path (including the JSON layer) must also succeed."""
        avocado: Avocado = c().from_dict(CODES_WITH_SINGLE_BIT_CODE)

        data: str = 'abacabad'
        result: Any = avocado.decompress(
            avocado.compress(data)
        )

        self.assertEqual(data, result)

    def test_avocado_python_round_trip_with_single_bit_code(self) -> None:
        """The full AvocadoPy path (including the JSON layer) must also succeed."""
        avocado: Avocado = python().from_dict(CODES_WITH_SINGLE_BIT_CODE)

        data: str = 'abacabad'
        result: Any = avocado.decompress(
            avocado.compress(data)
        )

        self.assertEqual(data, result)

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#
