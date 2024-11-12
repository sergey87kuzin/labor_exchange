from typing import Optional

from pydantic import BaseModel

from web.schemas import UserSchema
from web.schemas.job import JobSchema


class ResponseSchema(BaseModel):
    id: Optional[int] = None
    message: str
    user: Optional[UserSchema] = None
    job: Optional[JobSchema] = None


class ResponseUpdateSchema(BaseModel):
    message: str


class ResponseCreateSchema(BaseModel):
    user_id: int
    job_id: int
    message: str


class ShortResponseCreateSchema(BaseModel):
    message: str


class DeleteResponseSchema(BaseModel):
    id: int
