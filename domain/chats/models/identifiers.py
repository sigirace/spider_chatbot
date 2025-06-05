from pydantic_core import core_schema


class ChatId(str):
    def __new__(cls, value):
        return super().__new__(cls, str(value))

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_after_validator_function(
            function=cls,
            schema=core_schema.str_schema(),
        )
