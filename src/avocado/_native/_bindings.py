

import ctypes
import sys
from collections.abc import Mapping
from pathlib import Path

def _lib_path() -> Path:
    base = Path(__file__).parent / "lib"
    name = {
        "darwin": "libavocado.dylib",
        "linux":  "libavocado.so",
        "win32":  "avocado.dll",
    }[sys.platform]
    return base / name

_lib = ctypes.CDLL(str(_lib_path()))


# --- C-Structs (Spiegel von native/include/avocado/compress.h) -----------

class Codes_t(ctypes.Structure):
    _fields_ = [
        ("characters", ctypes.c_char_p),                 # char *
        ("codes", ctypes.POINTER(ctypes.c_char_p)),      # char **
        ("size", ctypes.c_int32),                        # int32_t
    ]


def codes_from_dict(mapping: Mapping[str, str]) -> Codes_t:
    """Baut aus einem {Zeichen: Code}-Mapping ein ``Codes_t``.

    Das i-te Zeichen in ``characters`` gehoert zum i-ten Code in ``codes``;
    die Reihenfolge entspricht der Iterationsreihenfolge des Mappings.

    Die zurueckgegebene Struktur haelt ihre Backing-Buffer selbst am Leben
    (ueber ctypes' internes ``_objects``), solange sie referenziert wird.
    Die Struktur darf also gefahrlos zurueckgegeben und weitergereicht werden.

    :param mapping: Zuordnung einzelner Zeichen zu ihrem Code-String.
    :raises ValueError: wenn ein Schluessel nicht genau ein Byte umfasst.
    :returns: eine gefuellte ``Codes_t``-Instanz.
    """
    size = len(mapping)

    characters = bytearray()
    codes = (ctypes.c_char_p * size)()
    
    for index, (character, code) in enumerate(mapping.items()):
        encoded_char = character.encode("utf-8")
        if len(encoded_char) != 1:
            raise ValueError(
                f"Schluessel muss genau ein Byte sein, war {character!r} "
                f"({len(encoded_char)} Bytes)"
            )
        characters += encoded_char
        codes[index] = code.encode("utf-8")

    result = Codes_t()
    result.characters = bytes(characters)
    result.codes = codes
    result.size = size
    return result


AVOCADO_Codec_t = ctypes.c_void_p                        # struct AVOCADO_Codec*

_lib.AVOCADO_Init.argtypes = [ctypes.POINTER(Codes_t)]   # const Codes_t *
_lib.AVOCADO_Init.restype = AVOCADO_Codec_t

_lib.AVOCADO_DeInit.argtypes = [ctypes.POINTER(AVOCADO_Codec_t)]   # AVOCADO_Codec_t *
_lib.AVOCADO_DeInit.restype = None                       # void

_lib.AVOCADO_Encode.argtypes = [
    AVOCADO_Codec_t,     # instance
    ctypes.c_char_p,     # const char *input
    ctypes.c_char_p,     # char *output  (beschreibbarer Puffer)
    ctypes.c_uint32,     # uint32_t size
]
_lib.AVOCADO_Encode.restype = ctypes.c_int32

_lib.AVOCADO_Decode.argtypes = [
    AVOCADO_Codec_t,     # instance
    ctypes.c_char_p,     # const char *input
    ctypes.c_char_p,     # char *output  (beschreibbarer Puffer)
    ctypes.c_uint32,     # uint32_t size
]
_lib.AVOCADO_Decode.restype = ctypes.c_int32

