from dataclasses import dataclass
from typing import Optional

from models.job import JobFull
from models.user import ShortUser


@dataclass
class ResponseWithUserAndJob:
    id: int
    message: str
    user: Optional[ShortUser]
    job: Optional[JobFull]
