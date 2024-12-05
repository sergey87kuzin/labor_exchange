from pydantic import ConfigDict

from web.schemas.base import to_lower_camel

# config для датаклассов
model_config = ConfigDict(
    populate_by_name=True,
    alias_generator=to_lower_camel,
)
