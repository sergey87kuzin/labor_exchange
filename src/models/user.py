from dataclasses import dataclass, field
from typing import Optional

from models.job import Job
from models.response import Response


@dataclass
class User:
    id: int
    name: str
    email: str
    is_company: bool
    hashed_password: Optional[str | None] = None

    jobs: Optional[list[Job]] = field(default_factory=list)
    responses: Optional[list[Response]] = field(default_factory=list)
