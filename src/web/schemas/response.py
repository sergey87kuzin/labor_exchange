from typing import Optional

from pydantic import BaseModel

from web.schemas.job import JobSchema
from web.schemas.user import UserSchema


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


class ResponseForUserSchema(BaseModel):
    id: int
    message: str


class DeleteResponseSchema(BaseModel):
    id: int
