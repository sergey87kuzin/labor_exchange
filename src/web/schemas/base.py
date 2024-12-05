from pydantic import BaseModel, ConfigDict


def to_lower_camel(string: str) -> str:
    """Трансфорфмировать имя поля из snake_case в camelCase."""

    camel = "".join(word.capitalize() for word in string.split("_"))
    return camel[0].lower() + camel[1:]


class CustomBaseModel(BaseModel):
    """config для моделей pydantic"""

    model_config: dict = ConfigDict(populate_by_name=True, alias_generator=to_lower_camel)
