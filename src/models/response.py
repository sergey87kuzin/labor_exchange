from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from models.base import model_config
from models.base_user import BaseUser
from models.job import Job


@dataclass(config=model_config)
class Response:
    id: int = Field(description="Идентификатор отклика")
    message: str | None = Field(default=None, description="Текст сопроводительного письма")
    user: Optional[BaseUser] = Field(default=None, description="Кандидат")  # noqa
    job: Optional[Job] = Field(default=None, description="Вакансия")  # noqa
    user_id: int | None = Field(default=None, description="Идентификатор кандидата")
