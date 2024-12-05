from pydantic import Field

from web.schemas.base import CustomBaseModel
from web.schemas.job import JobSchema
from web.schemas.user import UserSchema


class ResponseSchema(CustomBaseModel):
    """Класс отбражения откликов"""

    id: int | None = Field(default=None, description="Идентификатор отклика")
    message: str = Field(description="Текст сопроводительного письма")
    user: UserSchema | None = Field(default=None, description="Автор отклика")
    job: JobSchema | None = Field(default=None, description="Вакансия отклика")


class ResponseUpdateSchema(CustomBaseModel):
    """Класс для изменения отклика"""

    message: str = Field(description="Текст сопроводительного письма")


class ResponseCreateSchema(CustomBaseModel):
    """Класс создания отклика"""

    user_id: int = Field(default="Идентификатор кандидата")
    job_id: int = Field(default="Идентификатор вакансии")
    message: str = Field(description="Текст сопроводительного письма")


class DeleteResponseSchema(CustomBaseModel):
    """Класс удаления отклика"""

    id: int = Field(description="Идентификатор отклика")
