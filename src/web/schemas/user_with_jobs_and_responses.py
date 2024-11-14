from typing import Optional

from pydantic import BaseModel, EmailStr

from web.schemas.job import JobSchema
from web.schemas.response import ResponseForUserSchema


class UserSchemaWithJobAndResponse(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    is_company: bool

    jobs: Optional[list[JobSchema]]
    responses: Optional[list[ResponseForUserSchema]]
