from pydantic import EmailStr, Field

from web.schemas.base import CustomBaseModel


class TokenSchema(CustomBaseModel):
    """Класс для получения токенов"""

    access_token: str = Field(description="Токен доступа")
    refresh_token: str = Field(description="Токен восстановления")
    token_type: str = Field(description="Тип токена")


class LoginSchema(CustomBaseModel):
    """Класс для получения данных аутентификации"""

    email: EmailStr = Field(description="Адрес электронной почты")
    password: str = Field(description="Пароль")
