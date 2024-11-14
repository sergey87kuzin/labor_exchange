from dataclasses import asdict
from http import HTTPStatus

from fastapi import HTTPException

from repositories import UserRepository
from repositories.job_repository import JobRepository
from storage.sqlalchemy.tables import User
from tools.get_user_from_token import get_user_from_token
from web.schemas import JobCreateSchema, JobSchema, JobUpdateSchema
from web.schemas.filter import FilterSchema
from web.schemas.pagination import PaginationSchema


class JobService:
    def __init__(self, job_repository: JobRepository):
        self.job_repository = job_repository

    async def create_job(self, current_user: User, job_creation_data: JobCreateSchema) -> JobSchema:
        if not current_user or not current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Только компания может создавать вакансию"
            )
        if job_creation_data.user_id and job_creation_data.user_id != current_user.id:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Можно создать вакансию только от имени своей компании",
            )
        job_creation_data.user_id = current_user.id
        job_model = await self.job_repository.create(job_creation_data)
        return JobSchema(**asdict(job_model))

    async def jobs_list(
        self,
        pagination: PaginationSchema,
        jobs_filter: FilterSchema,
        user_repository: UserRepository,
        token: str = None,
    ) -> list[JobSchema]:
        if token:
            current_user = await get_user_from_token(token, user_repository)
        else:
            current_user = None
        # компания может видеть только свои вакансии
        if current_user and current_user.is_company:
            jobs_filter.company_id = current_user.id
        jobs_from_db = await self.job_repository.retrieve_many(
            limit=pagination.limit, skip=pagination.skip, job_filter=jobs_filter
        )
        return [JobSchema(**asdict(job)) for job in jobs_from_db]

    async def job_details(
        self, job_id: int, user_repository: UserRepository, token: str = None
    ) -> JobSchema | None:
        if token:
            current_user = await get_user_from_token(token, user_repository)
        else:
            current_user = None
        kwargs = {"id": job_id}
        # компания может видеть только свои вакансии
        if current_user and current_user.is_company:
            kwargs["user_id"] = current_user.id
        job_model = await self.job_repository.retrieve(**kwargs)
        if not job_model:
            return None
        return JobSchema(**asdict(job_model))

    async def job_delete(self, job_id: int, current_user: User) -> JobSchema | None:
        if not current_user or not current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Удалять вакансии могут только компании"
            )
        job = await self.job_repository.delete(job_id, user_id=current_user.id)
        if not job:
            return None
        return JobSchema(**asdict(job))

    async def job_update(
        self, job_id: int, current_user: User, job_update_data: JobUpdateSchema
    ) -> JobSchema | None:
        if not current_user or not current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Редактировать вакансии может только компания",
            )
        job = await self.job_repository.update(job_id, current_user.id, job_update_data)
        if not job:
            return None
        return JobSchema(**asdict(job))
