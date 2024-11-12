import decimal
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from models.user import ShortUser


@dataclass
class JobToRetrieve:
    id: int
    title: str
    description: str
    salary_from: decimal.Decimal
    salary_to: decimal.Decimal
    is_active: bool
    created_at: datetime
    user: Optional[ShortUser]
