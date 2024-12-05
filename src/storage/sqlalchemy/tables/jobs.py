import decimal
from datetime import datetime

from sqlalchemy import DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.sqlalchemy.client import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, comment="Идентификатор вакансии")
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), comment="Идентификатор пользователя"
    )

    title: Mapped[str] = mapped_column(String(100), comment="Название вакансии")
    description: Mapped[str] = mapped_column(comment="Описание вакансии")
    salary_from: Mapped[decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), comment="Зарплата от"
    )
    salary_to: Mapped[decimal] = mapped_column(
        DECIMAL(precision=10, scale=2), comment="Зарплата до"
    )
    is_active: Mapped[bool] = mapped_column(comment="Активна ли вакансия")
    created_at: Mapped[datetime] = mapped_column(
        comment="Дата создания записи", default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="jobs")  # noqa
    responses: Mapped["Response"] = relationship(back_populates="job")  # noqa
