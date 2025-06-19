from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from sqlmodel import SQLModel

class CamelModel(SQLModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True
    )
