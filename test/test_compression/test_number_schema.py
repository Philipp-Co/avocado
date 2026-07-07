
#
# ---------------------------------------------------------------------------------------------------------------------
#
from unittest import TestCase
from time import time_ns
from avocado.avocado import c, python, AvocadoPy, Avocado, AvocadoC 
from marshmallow import Schema, fields, validate
from random import random
from json import dumps
#
# ---------------------------------------------------------------------------------------------------------------------
#

class Schema0(Schema):
    integer_field = fields.Integer()
    pass

class Schema1(Schema):
    float_field = fields.Float()
    pass

class Schema2(Schema):
    field = fields.List(fields.Float(), validate=[validate.Length(max=5)])

#
# ---------------------------------------------------------------------------------------------------------------------
#
class TestCompression(TestCase):


    def test_schema_0(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema0()
            )
        )
        for integer_item in range(0, 1000):
            daten: Dict[str, Any] = {
                'integer_field': integer_item,
            }
            output: Dict[str, Any] = b.decompress(
                b.compress(
                    daten
                )
            )
            self.assertDictEqual(daten, output)
        pass

    def test_schema_1(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema1()
            )
        )
        item: float = -1.0
        while item <= 1.0:
            daten: Dict[str, Any] = {
                'float_field': item,
            }
            output: Dict[str, Any] = b.decompress(
                b.compress(
                    daten
                )
            )
            self.assertDictEqual(daten, output)
            item += 0.1
        pass
    
    def test_schema_1_1(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema1()
            )
        )
        item: float = -99999.0
        while item <= 99999.0:
            item_with_fractions = item + random()
            daten: Dict[str, Any] = {
                'float_field': item,
            }
            output: Dict[str, Any] = b.decompress(
                b.compress(
                    daten
                )
            )
            self.assertDictEqual(daten, output)
            item += 1000.0
        pass

    def test_schema_2(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema2()
            )
        )
        
        for _ in range(0, 100):
            
            alist: [float] = []
            for _ in range(0, 10):
                item_with_fractions = random() * 100.0 + random()
                alist.append(item_with_fractions)

            daten: Dict[str, Any] = {
                'field': alist,
            }
            output: Dict[str, Any] = b.decompress(
                b.compress(
                    daten
                )
            )
            self.assertDictEqual(daten, output)
        pass

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#
