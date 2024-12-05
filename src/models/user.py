from pydantic import Field
from pydantic.dataclasses import dataclass

from models.base import model_config
from models.job import Job
from models.response import Response


@dataclass(config=model_config)
class User:
    id: int = Field(description="Идентификатор пользователя")
    name: str = Field(description="Имя пользователя")
    email: str = Field(description="Адрес электронной почты")
    is_company: bool = Field(description="Активен")
    hashed_password: str | None = Field(default=None, description="Пароль")

    jobs: list[Job] | None = Field(default=[], description="Вакансии")
    responses: list[Response] | None = Field(default=[], description="Отклики")
