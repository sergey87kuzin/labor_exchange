from datetime import datetime

from pydantic import Field

from web.schemas.base import CustomBaseModel


class FilterSchema(CustomBaseModel):
    """Класс параметров фильтрации списка вакансий"""

    salary_from: int | None = Field(default=None, description="Зарплата от")
    salary_to: int | None = Field(default=None, description="Зарплата до")
    created_at: datetime | None = Field(default=None, description="Дата создания вакансии, от")
    company_id: int | None = Field(default=None, description="Идентификатор компании")
    title: str | None = Field(default=None, description="Название вакансии")
