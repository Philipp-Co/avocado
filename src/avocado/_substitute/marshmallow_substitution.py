
#
# ---------------------------------------------------------------------------------------------------------------------
#
from marshmallow import Schema, fields, validate 
from marshmallow.fields import Field

#
# ---------------------------------------------------------------------------------------------------------------------
#

class MarshmallowSubstitutor:
   
    def __init__(self, schema: Schema) -> None:
        self.__current_a = 'a'
        self.__schema: Schema = schema
        pass
    
    def _generate_substitutions_for_schema(self, name: str, schema: Schema, output: Dict[str, str]) -> None:
        output.update(
            {
                name: self.__current_a
            }
        )
        self.__current_a += 'a'
        for name, field in schema.fields.items():
            if isinstance(field, fields.Nested):
                self._generate_substitutions_for_schema(name, field.schema, output)
            elif isinstance(field, Field):
                self._generate_substitutions_for_field(name, field, output)
            else:
                raise AssertionError
        pass

    def _generate_substitutions_for_field(self, name: str, field: Field, output: Dict[str, str]) -> None:
        output.update(
            {
                name: self.__current_a,
            }
        )
        self.__current_a += 'a'
        pass

    def generate_substitutions(self, schema: Schema) -> Dict[str, str]:
        output: Dict[str, str] = {}
        for name, field in schema.fields.items():
            if isinstance(field, fields.Nested):
                self._generate_substitutions_for_schema(name, field.schema, output)
            elif isinstance(field, fields.Field):
                self._generate_substitutions_for_field(name, field, output)
            else:
                raise AssertionError
        return output

    def _substitute(self, data: Any, schema: Schema, subs: Any) -> Any:
        output = {}
        for name, field in schema.fields.items():
            if isinstance(field, fields.Nested):
                output[subs[name]] = self._substitute(data[name], field.schema, subs) 
            else:
                output[subs[name]] = data[name] 
        return output

    def substitute(self, data: Any) -> Any:
        self.__current_a = 'a'
        output = {}
        subsitutions: Dict[str, str] = self.generate_substitutions(self.__schema) 
        return self._substitute(data, self.__schema, subsitutions)


    def _inverse_substitution(self, data: Any, schema: Schema, subs: Any, invsubs: Any) -> Any:
        output = {}
        for name, field in schema.fields.items():
            if isinstance(field, fields.Nested):
                output[name] = self._inverse_substitution(data[subs[name]], field.schema, subs, invsubs) 
            else:
                output[name] = data[subs[name]] 
        return output

    def inverse_substitution(self, data: Any) -> Any:
        self.__current_a = 'a'
        output = {}
        subsitutions: Dict[str, str] = self.generate_substitutions(self.__schema) 
        inverse_substitutions = {}
        for key in subsitutions:
            inverse_substitutions[subsitutions[key]] = key
        return self._inverse_substitution(data, self.__schema, subsitutions, inverse_substitutions)

    pass

#
# ---------------------------------------------------------------------------------------------------------------------
#

