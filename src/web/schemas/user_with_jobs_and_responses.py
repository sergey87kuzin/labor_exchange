from typing import Optional

from pydantic import BaseModel, EmailStr

from web.schemas.job import ShortJobSchema
from web.schemas.response import ResponseForUserSchema


class UserSchemaWithJobAndResponse(BaseModel):
    id: Optional[int] = None
    name: str
    email: EmailStr
    is_company: bool

    jobs: Optional[list[ShortJobSchema]]
    responses: Optional[list[ResponseForUserSchema]]
