from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Job:
    id: int


@dataclass
class JobFull:
    id: int
    title: str
    description: str
    salary_from: Decimal
    salary_to: Decimal
    is_active: bool
