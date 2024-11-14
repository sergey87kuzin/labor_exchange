from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class Job:
    id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool
    user_id: Optional[int] = None
