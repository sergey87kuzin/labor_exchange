from pydantic import EmailStr, Field, model_validator
from typing_extensions import Self

from web.schemas.base import CustomBaseModel


class BaseUserSchema(CustomBaseModel):
    """Базовый класс пользователя"""

    name: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Адрес электронной почты")
    is_company: bool = Field(default=False, description="Является ли компанией")


class UserSchema(BaseUserSchema):
    """Класс отображения пользователя"""

    id: int | None = Field(default=None, description="Идентификатор пользователя")

    jobs: list["JobSchema"] | None = Field(default=[], description="Список вакансий")  # noqa
    responses: list["ResponseSchema"] | None = Field(  # noqa
        default=[], description="Список откликов"
    )


class UserUpdateSchema(CustomBaseModel):
    name: str | None = Field(default=None, description="Имя пользователя")
    email: EmailStr | None = Field(default=None, description="Адрес электронной почты")
    is_company: bool | None = Field(default=None, description="Является ли компанией")


class UserCreateSchema(BaseUserSchema):
    """Класс для создания пользователя"""

    password: str = Field(description="Пароль", min_length=8)
    password2: str = Field(description="Пароль повторно")

    @model_validator(mode="after")
    def password_match(self) -> Self:
        pw1 = self.password
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("Пароли не совпадают")
        return self
