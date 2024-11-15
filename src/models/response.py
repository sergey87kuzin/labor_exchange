from dataclasses import dataclass
from typing import Optional


@dataclass
class Response:
    id: int
    message: Optional[str | None]
    user: Optional["User"] = None  # noqa
    job: Optional["Job"] = None  # noqa
    user_id: Optional[int] = None
