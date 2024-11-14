from dataclasses import dataclass
from typing import Optional


@dataclass
class Response:
    id: int
    message: Optional[str]
