
#
# ---------------------------------------------------------------------------------------------------------------------
#
from unittest import TestCase

from random import random


from avocado.avocado import Avocado, python, c
from avocado._substitute.marshmallow_substitution import MarshmallowSubstitutor

from marshmallow import Schema, fields, validate
from json import dumps
from pathlib import Path

#
# ---------------------------------------------------------------------------------------------------------------------
#

class TestNested(Schema):
    integer_field = fields.Integer(
        allow_none=True,
        validate=[
            0, 2
        ]
    )
    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

class TestSchema(Schema):
    integer_field = fields.Integer(
        allow_none=True,
        validate=[
            0, 2
        ]
    )
    nested_field = fields.Nested(TestNested())
    pass
#
# ---------------------------------------------------------------------------------------------------------------------
#

class TestFilePy(TestCase):
    
    def setUp(self):
        path: Path = Path('./test_file.avocado')
        path.unlink(missing_ok=True)
        pass

    def tearDown(self):
        path: Path = Path('./test_file.avocado')
        path.unlink(missing_ok=True)
        pass

    def runTest(self):
        codes = Avocado.generate_codes(
            TestSchema()
        )
        a: Avocado = python().from_dict(codes)
        a.to_file('./test_file.avocado')
        b: Avocado = python().from_file('./test_file.avocado')
        self.assertCountEqual(
            a.codes(), b.codes()
        )
        pass

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#

class TestFileC(TestCase):
    
    def setUp(self):
        path: Path = Path('./test_file.avocado')
        path.unlink(missing_ok=True)
        pass

    def tearDown(self):
        path: Path = Path('./test_file.avocado')
        path.unlink(missing_ok=True)
        pass

    def runTest(self):
        codes = Avocado.generate_codes(
            TestSchema()
        )
        a: Avocado = c().from_dict(codes)
        a.to_file('./test_file.avocado')
        b: Avocado = c().from_file('./test_file.avocado')
        self.assertCountEqual(
            a.codes(), b.codes()
        )
        pass

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#
