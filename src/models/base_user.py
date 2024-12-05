from pydantic import Field
from pydantic.dataclasses import dataclass

from models.base import model_config


@dataclass(config=model_config)
class BaseUser:
    """Базовый класс пользователя для импорта в другие модели"""

    id: int = Field(description="Идентификатор пользователя")
    name: str = Field(description="Имя пользователя")
    email: str = Field(description="Адрес электронной почты")
    is_company: bool = Field(description="Активен")
