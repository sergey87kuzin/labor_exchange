from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from models.base import model_config
from models.base_user import BaseUser


@dataclass(config=model_config)
class Job:
    id: int = Field(description="Идентификатор вакансии")
    title: str = Field(description="Название вакансии")
    description: str = Field(description="Описание вакансии")
    salary_from: Decimal = Field(description="Зарплата от")
    salary_to: Decimal = Field(description="Зарплата до")
    is_active: bool = Field(description="Активна")
    created_at: datetime | None = Field(default=None, description="Создана в")
    user_id: int | None = Field(default=None, description="Идентификатор компании")
    user: Optional[BaseUser] = Field(default=None, description="Компания")  # noqa
