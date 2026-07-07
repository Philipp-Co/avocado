
#
# ---------------------------------------------------------------------------------------------------------------------
#
from unittest import TestCase
from random import random


from avocado.avocado import Avocado, python, AvocadoPy
from avocado._substitute.marshmallow_substitution import MarshmallowSubstitutor

from marshmallow import Schema, fields, validate
from json import dumps, loads

#
# ---------------------------------------------------------------------------------------------------------------------
#
class TestNested2(Schema):
    haha = fields.String(validate=[validate.OneOf(['asda', 'lkjwe', 'avub'])])
    pass

class TestNested(Schema):

    datetime_field = fields.DateTime()
    string_field = fields.String(
        validate=[
            validate.OneOf(['Test', 'haka'])
        ]
    )
    list_field = fields.List(fields.Integer(), validate=[validate.Length(max=5)])
    nested_field = fields.Nested(TestNested2())


class TestSchema(Schema):

    integer_field = fields.Integer(
        allow_none=True,
        validate=[
            0, 2
        ]
    )
    boolean_field = fields.Boolean()
    nested_field = fields.Nested(TestNested())


    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
class TestGenerateCodes(TestCase):

    def runTest(self):
        token = Avocado.generate_codes(
            TestSchema()    
        )
        c: Avocado = python().from_dict(token)
        self.assertTrue(isinstance(c, AvocadoPy))
        original_data = {
            'integer_field': None,
            'boolean_field': True,
            'nested_field': {
                'datetime_field': '2379-01-01T23:34:56,983+08:01',
                'string_field': 'Test',
                'list_field': [1 for i in range(0, 10)],
                'nested_field': {
                    'haha': 'asda',
                }
            }
        }        
        substituted_data = MarshmallowSubstitutor(TestSchema()).substitute(
            original_data,
        )
        compressed_data = c.compress(
            substituted_data
        )
        a = c.decompress(compressed_data)
        data = MarshmallowSubstitutor(TestSchema()).inverse_substitution(
            a
        )
        
        self.assertCountEqual(
            original_data,
            data
        )
        pass

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
