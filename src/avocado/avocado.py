
#
# ---------------------------------------------------------------------------------------------------------------------
#
from enum import StrEnum
from ._python_implementation import AvocadoPy
from ._c_implementation import AvocadoC
from ._avocado_base import Avocado

#
# ---------------------------------------------------------------------------------------------------------------------
#

__all__ = [
    'Avocado',
]

#
# ---------------------------------------------------------------------------------------------------------------------
#

def python() -> Avocado:
    return AvocadoPy()

#
# ---------------------------------------------------------------------------------------------------------------------
#
def c() -> Avocado:
    return AvocadoC()

#
# ---------------------------------------------------------------------------------------------------------------------
#

class AvocadoImplementation(StrEnum):
    C = 'c'
    Python = 'python'
    pass

def create(implementation: AvocadoImplementation=AvocadoImplementation.C) -> Avocado:
    try:
        return AvocadoC()
    except (OSError, ImportError):
        return AvocadoPy()

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
