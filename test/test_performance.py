
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

class TestNested(Schema):

    string_field = fields.String(
        validate=[
            validate.OneOf(['Test', 'haka'])
        ]
    )
    pass

class TestSchema(Schema):

    integer_field = fields.Integer()
    boolean_field = fields.Boolean()
    nested_field = fields.Nested(TestNested())
    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
class TestPerformance(TestCase):


    def test_run_1000_times(self) -> None:
        N: int = 1000
        daten = {
            'integer_field': 0,
            'boolean_field': True,
            'nested_field': {
                'string_field': 'haka',
            },
        }
        a: Avocado = python().from_dict(
            Avocado.generate_codes(
                TestSchema()
            )
        )
        start = time_ns()
        for _ in range(0, N):
            a.decompress(
                a.compress(
                    daten
                )
            ) 
        end = time_ns()
        py_time_taken_in_ms = (end - start) / (1000 * 1000)
        py_avg_time_taken_by_1_run = py_time_taken_in_ms / N

        b: Avocado = c().from_dict(
            Avocado.generate_codes(
                TestSchema()
            )
        )
        start = time_ns()
        for _ in range(0, N):
            b.decompress(
                b.compress(
                    daten
                )
            ) 
        end = time_ns()
        c_time_taken_in_ms = (end - start) / (1000 * 1000)
        c_avg_time_taken_by_1_run = c_time_taken_in_ms / N

        self.assertTrue(
            py_time_taken_in_ms > c_time_taken_in_ms,
            msg=f'Py {py_time_taken_in_ms}, C {c_time_taken_in_ms}'
        )
        self.assertTrue(
            py_avg_time_taken_by_1_run > c_avg_time_taken_by_1_run
        )
        pass

    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#
