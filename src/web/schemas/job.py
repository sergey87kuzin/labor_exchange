from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from web.schemas.user import UserSchema


class JobBaseSchema(BaseModel):
    salary_from: Decimal = Field(ge=0.01, le=99999999.99, decimal_places=2)
    salary_to: Decimal = Field(ge=0.01, le=99999999.99, decimal_places=2)
    title: str

    @field_validator("title")
    def check_title_length(cls, value):
        if value and len(value) > 100:
            raise ValueError("Слишком длинное название")
        return value

    @model_validator(mode="after")
    def salary_match(self) -> Self:
        if self.salary_from > self.salary_to:
            raise ValueError("salary from has to be less or equal then salary to")
        return self


class JobSchema(JobBaseSchema):
    id: Optional[int] = None
    description: str
    is_active: bool = False
    created_at: Optional[datetime] = None
    user: Optional[UserSchema] = None


class JobUpdateSchema(JobBaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class JobCreateSchema(JobBaseSchema):
    user_id: Optional[int] = None
    description: str
    is_active: Optional[bool] = None
