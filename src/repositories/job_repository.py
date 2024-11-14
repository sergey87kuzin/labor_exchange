from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models.job_with_user import JobToRetrieve as JobModel
from models.user import User as UserModel
from storage.sqlalchemy.tables import Job
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
        return self.__to_job_model(job_from_db=job, include_relations=False)

    async def retrieve(self, **kwargs) -> JobModel:
        async with self.session() as session:
            query = select(Job).filter_by(**kwargs).limit(1).options(joinedload(Job.user))

            res = await session.execute(query)
            job_from_db = res.scalars().first()

        job_model = self.__to_job_model(job_from_db=job_from_db, include_relations=True)
        return job_model

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
            model = self.__to_job_model(job_from_db=job, include_relations=True)
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

        new_job = self.__to_job_model(updated_job, include_relations=False)
        return new_job

    async def delete(self, job_id: int, user_id: int) -> JobModel | None:
        async with self.session() as session:
            query = select(Job).filter_by(id=job_id, user_id=user_id).limit(1)
            res = await session.execute(query)
            job_from_db = res.scalars().first()

            if job_from_db:
                await session.delete(job_from_db)
            else:
                return None

        return self.__to_job_model(job_from_db, include_relations=False)

    @staticmethod
    def __to_job_model(job_from_db: Job, include_relations: bool = False) -> JobModel | None:
        if not job_from_db:
            return None

        job_model = JobModel(
            id=job_from_db.id,
            title=job_from_db.title,
            description=job_from_db.description,
            salary_from=job_from_db.salary_from,
            salary_to=job_from_db.salary_to,
            is_active=job_from_db.is_active,
            created_at=job_from_db.created_at,
            user=None,
        )
        if include_relations:
            user = UserModel(
                id=job_from_db.id,
                name=job_from_db.user.name,
                email=job_from_db.user.email,
                is_company=job_from_db.user.is_company,
            )
            job_model.user = user

        return job_model
