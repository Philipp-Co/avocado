from marshmallow import Schema, fields, validate 
from marshmallow.fields import Field
from typing import Dict, Any, Tuple, Set
from .generate_codes import generate_huffman_codes, _build_huffman_tree



class SchemaCodeGenerator:

    @staticmethod
    def _handle_datetime_field(name: str, field: Field, output: Dict[str, int]):
        for item in ['T', '+', '-', '"', ':', ','] + [str(i) for i in range(0, 10)]:
            output.update(
                {
                    item: output.get(item, 0) + 1
                }
            )
        pass
    
    @staticmethod
    def _handle_list_field(name: str, field: Field, output: Dict[str, int]):
        for item in ['[', ']', ',',]:
            output.update(
                {
                    item: output.get(item, 0) + 1
                }
            )
        if isinstance(field, fields.List):
            if isinstance(field.inner, fields.Nested):
                for _ in range(0, 10):
                    nested_schema = field.inner.schema
                    SchemaCodeGenerator._generate_tokens_from_schema(nested_schema, output)
                    pass
            else: 
                for _ in range(0, 10):
                    SchemaCodeGenerator._generate_tokens_from_field(name, field.inner, output)
        pass

    @staticmethod
    def _handle_string_field(name: str, field: Field, output: Dict[str, int]):
        valid_string_field: bool = False
        if len(field.validators) == 1:
            for v in field.validators:
                if isinstance(v, validate.OneOf):
                    valid_string_field = True
                    for item in v.choices:
                        for c in item:
                            output.update(
                                {
                                    c: output.get(c, 0) + 1
                                }
                            )
            if not valid_string_field:
                raise AvocadoStringFoundException(
                    f'The given Fields is not valid. The value Range is too big.'
                )
        else:
            raise AvocadoStringFoundException(
                'String found. Use another Compressionmethod if you want to compress universal Strings.'
            )
        output.update(
            {
                '"': output.get('"', 0) + 1
            }
        )
        pass
    
    @staticmethod
    def _handle_number_field(name: str, field: Field, output: Dict[str, int]):
        for item in field.validators:
            if isinstance(item, validate.OneOf):
                for choice in item.choices:
                    for c in str(choice):
                        output.update(
                            {
                                c: output.get(c, 0) + 1
                            }
                        )
        for i in range(0, 10):
            output.update(
                {
                    str(i): output.get(str(i), 0) + 1
                }
            )

        for item in ['.', 'e', 'E', '+', '-', ',']:
            output.update(
                {
                    item: output.get(item, 0) + 1
                }
            )
        pass
    
    @staticmethod
    def _handle_boolean_field(name: str, field: Field, output: Dict[str, int]):
        for item in ['true', 'false']:
            for c in item:
                output.update(
                    {
                        c: output.get(c, 0) + 1
                    }
                )
        pass

    @staticmethod
    def _generate_tokens_from_field(name: str, field: Field, output: Dict[str, int]):
        for c in name:
            output.update(
                {
                    c:
                    output.get(
                        c, 0
                    ) + 1, 
                },
            )
        if isinstance(field, fields.Nested):
            nested_schema: Schema = field.schema 
            for item in [
                '{', '}', ':', ',', '"', 
            ]:
                output.update(
                    {
                        item: output.get(item, 0) + 2
                    }
                )
            SchemaCodeGenerator._generate_tokens_from_schema(
                nested_schema,
                output
            )
        elif isinstance(field, fields.Integer) or isinstance(field, fields.Float):
            SchemaCodeGenerator._handle_number_field(name, field, output)
        elif isinstance(field, fields.Boolean):
            SchemaCodeGenerator._handle_boolean_field(name, field, output)
        elif isinstance(field, fields.String):
            SchemaCodeGenerator._handle_string_field(name, field, output)
        elif isinstance(field, fields.Date) or isinstance(field, fields.DateTime):
            SchemaCodeGenerator._handle_datetime_field(name, field, output)
        elif isinstance(field, fields.List):
            SchemaCodeGenerator._handle_list_field(name, field, output)
        if field.allow_none:
            for item in ['n', 'u', 'l', 'l']:
                output.update(
                    {
                        item:
                        output.get(item, 0) + 1,
                    },
                )
        pass
    
    @staticmethod
    def _generate_tokens_from_schema(schema: Schema, output: Dict[str, int]):
        field: Field
        for name, field in schema.fields.items():
            SchemaCodeGenerator._generate_tokens_from_field(name, field, output)

    @staticmethod
    def generate_codes_from_schema(schema: Schema) -> Dict[str, str]:
        output: Dict[str, int] = {}
        SchemaCodeGenerator._generate_tokens_from_schema(schema, output)
        for item in [
            '{', '}', ':', ',', '"', 
        ]:
            output.update(
                {
                    item: output.get(item, 0) + 2
                }
            )
        return generate_huffman_codes(
            _build_huffman_tree(
                [key for key in output], [output[key] for key in output] 
            ),
        )

    pass

