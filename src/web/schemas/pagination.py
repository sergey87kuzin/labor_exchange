from typing import Optional

from pydantic import BaseModel, Field


class PaginationSchema(BaseModel):
    limit: Optional[int] = Field(
        gt=0, le=100, description="Количество записей в запросе", default=100
    )
    skip: Optional[int] = Field(ge=0, description="Пропущено записей в начале", default=0)
