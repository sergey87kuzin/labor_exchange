from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models.job_with_user import JobToRetrieve as JobModel
from storage.sqlalchemy.tables import Job
from tools.to_model import ToModel
from web.schemas.filter import FilterSchema
from web.schemas.job import JobCreateSchema, JobUpdateSchema


class JobRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, job_to_create: JobCreateSchema) -> JobModel:
        async with self.session() as session:

            job = Job(**job_to_create.dict())

            session.add(job)
            await session.commit()
        return ToModel().to_job_model(job_from_db=job, include_relations=False)

    async def retrieve(self, **kwargs) -> JobModel:
        async with self.session() as session:
            query = select(Job).filter_by(**kwargs).limit(1).options(joinedload(Job.user))

            res = await session.execute(query)
            job_from_db = res.scalars().first()

        return ToModel().to_job_model(job_from_db=job_from_db, include_relations=True)

    async def retrieve_many(
        self,
        job_filter: FilterSchema,
        limit: int = 100,
        skip: int = 0,
    ) -> list[JobModel]:
        async with self.session() as session:
            query = select(Job).limit(limit).offset(skip).options(joinedload(Job.user))
            if job_filter.salary_from:
                query = query.filter(Job.salary_to >= job_filter.salary_from)
            if job_filter.salary_to:
                query = query.filter(Job.salary_from <= job_filter.salary_to)
            if job_filter.created_at:
                query = query.filter(Job.created_at >= job_filter.created_at)
            if job_filter.company_id:
                query = query.filter_by(user_id=job_filter.company_id)
            if job_filter.title:
                query = query.filter(Job.title.like(f"%{job_filter.title}%"))
            res = await session.execute(query)
            jobs_from_db = res.scalars().all()

        jobs_model = []
        for job in jobs_from_db:
            model = ToModel().to_job_model(job_from_db=job, include_relations=True)
            jobs_model.append(model)

        return jobs_model

    async def update(
        self, job_id: int, user_id: int, job_update_dto: JobUpdateSchema
    ) -> JobModel | None:
        async with self.session() as session:
            query = select(Job).filter_by(id=job_id, user_id=user_id).limit(1)
            res = await session.execute(query)
            job_from_db = res.scalars().first()

            if not job_from_db:
                return None

            update_data = {
                key: value for key, value in job_update_dto.dict().items() if value is not None
            }
            query = update(Job).filter_by(id=job_id).values(**update_data).returning(Job)
            result = await session.execute(query)
            updated_job = result.scalars().first()

        return ToModel().to_job_model(job_from_db=updated_job, include_relations=False)

    async def delete(self, job_id: int, user_id: int) -> JobModel | None:
        async with self.session() as session:
            query = select(Job).filter_by(id=job_id, user_id=user_id).limit(1)
            res = await session.execute(query)
            job_from_db = res.scalars().first()

            if job_from_db:
                await session.delete(job_from_db)
            else:
                return None

        return ToModel().to_job_model(job_from_db=job_from_db, include_relations=False)
