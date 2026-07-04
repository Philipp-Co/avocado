
#
# ---------------------------------------------------------------------------------------------------------------------
#
from unittest import TestCase
from time import time_ns
from avocado.avocado import c, python, AvocadoPy, Avocado, AvocadoC 
from marshmallow import Schema, fields, validate
#
# ---------------------------------------------------------------------------------------------------------------------
#

class Schema0(Schema):
    integer_field = fields.Integer()
    boolean_field = fields.Boolean()
    string_field = fields.String(validate=[validate.OneOf(['foo', 'bar'])])
    pass

class Schema1(Schema):
    nested_field = fields.Nested(Schema0())
    pass

class Schema2(Schema):
    list_field = fields.List(fields.Nested(Schema1()))
    pass

class Schema3(Schema):
    nullable_integer_field = fields.Integer(allow_none=True)
    pass

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
        for string_item in ['foo', 'bar']:
            for boolean_value in [True, False]:
                for integer_item in range(0, 10):
                    daten: Dict[str, Any] = {
                        'integer_field': integer_item,
                        'boolean_field': boolean_value,
                        'string_field': string_item,
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
        for string_item in ['foo', 'bar']:
            for boolean_value in [True, False]:
                for integer_item in range(0, 10):
                    daten: Dict[str, Any] = {
                        'nested_field': {
                            'integer_field': integer_item,
                            'boolean_field': boolean_value,
                            'string_field': string_item,
                        }
                    }
                    output: Dict[str, Any] = b.decompress(
                        b.compress(
                            daten
                        )
                    )
                    self.assertDictEqual(daten, output)
        pass

    def test_schema_2(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema2()
            )
        )
        for string_item in ['foo', 'bar']:
            for boolean_value in [True, False]:
                for integer_item in range(0, 10):
                    daten: Dict[str, Any] = {
                        'list_field' : [
                            {
                                'nested_field': {
                                    'integer_field': integer_item,
                                    'boolean_field': boolean_value,
                                    'string_field': string_item,
                                },
                            },
                            {
                                'nested_field': {
                                    'integer_field': integer_item,
                                    'boolean_field': boolean_value,
                                    'string_field': string_item,
                                },
                            },
                        ],
                    }
                    output: Dict[str, Any] = b.decompress(
                        b.compress(
                            daten
                        )
                    )
                    self.assertDictEqual(daten, output)
        pass
    
    def test_schema_3(self) -> None:
        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                Schema3()
            )
        )
        daten: Dict[str, Any] = {
            'nullable_integer_field': None,
        }
        output: Dict[str, Any] = b.decompress(
            b.compress(
                daten
            )
        )
        self.assertDictEqual(daten, output)

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#
