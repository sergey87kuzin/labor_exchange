from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FilterSchema(BaseModel):
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    created_at: Optional[datetime] = None
    company_id: Optional[int] = None
    title: Optional[str] = None
