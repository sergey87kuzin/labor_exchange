from dataclasses import dataclass
from typing import Optional

from models import Job
from models.user import User


@dataclass
class ResponseWithUserAndJob:
    id: int
    message: str
    user: Optional[User]
    job: Optional[Job]
    user_id: Optional[int] = None
