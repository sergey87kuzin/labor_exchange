from datetime import datetime
from decimal import Decimal

from pydantic import Field, model_validator
from typing_extensions import Self

from web.schemas.base import CustomBaseModel
from web.schemas.user import UserSchema


class JobBaseSchema(CustomBaseModel):
    """Базовый класс вакансии"""

    salary_from: Decimal = Field(
        ge=0.01,
        le=99999999.99,
        decimal_places=2,
        description="Зарплата от",
    )
    salary_to: Decimal = Field(
        ge=0.01,
        le=99999999.99,
        decimal_places=2,
        description="Зарплата до",
    )
    title: str = Field(description="Название вакансии")
    description: str = Field(description="Описание вакансии")

    @model_validator(mode="after")
    def salary_match(self) -> Self:
        if self.salary_from > self.salary_to:
            raise ValueError("Зарплата от не должна превышать зарплату до")
        return self


class JobSchema(JobBaseSchema):
    """Класс для получения данных о вакансии"""

    id: int | None = Field(default=None, description="Идентификатор вакансии")
    is_active: bool = Field(
        default=False,
        description="Вакансия активна",
    )
    created_at: datetime | None = Field(
        default=None,
        description="Создана в",
    )
    user: UserSchema | None = Field(default=None, description="Компания")


class JobUpdateSchema(JobBaseSchema):
    """Класс для изменения вакансии"""

    title: str | None = Field(default=None, description="Название вакансии")
    description: str | None = Field(default=None, description="Описание вакансии")
    is_active: bool | None = Field(
        default=None,
        description="Вакансия активна",
    )


class JobCreateSchema(JobBaseSchema):
    """Класс для создания вакансии"""

    user_id: int | None = Field(default=None, description="Идентификатор компании")
    is_active: bool | None = Field(
        default=None,
        description="Вакансия активна",
    )
