from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models import Response as ShortResponseModel
from models import ResponseWithUserAndJob as ResponseModel
from models.job import JobFull as JobModel
from models.user import ShortUser as UserModel
from storage.sqlalchemy.tables import Response
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema


class ResponseRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, response_to_create: ResponseCreateSchema) -> ResponseModel:
        async with self.session() as session:

            response = Response(**response_to_create.dict())

            session.add(response)
            await session.commit()

        return self.__to_response_model(response_from_db=response, with_user=False, with_job=False)

    async def retrieve(
        self, response_id: int, user_id: int, is_company: bool = False
    ) -> ResponseModel:
        async with self.session() as session:
            query = select(Response).filter_by(id=response_id).limit(1)
            if is_company:
                query = query.filter(Response.job.user_id == user_id).options(
                    joinedload(Response.user)
                )
            else:
                query = query.filter_by(user_id=user_id).options(joinedload(Response.job))

            res = await session.execute(query)
            response_from_db = res.scalars().first()
        if not response_from_db:
            raise ValueError("Отклик не найден")
        if is_company:
            with_user = True
            with_job = False
        else:
            with_user = False
            with_job = True
        response_model = self.__to_response_model(
            response_from_db=response_from_db, with_user=with_user, with_job=with_job
        )
        return response_model

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, job_id: int = 0, user_id: int = 0
    ) -> list[ResponseModel]:
        if job_id <= 0 and user_id <= 0:
            raise ValueError("Не заданы параметры фильтрации откликов")
        if job_id > 0 and user_id > 0:
            raise ValueError("Параметры фильтрации откликов заданы некорректно")
        async with self.session() as session:
            query = select(Response).limit(limit).offset(skip)
            if job_id > 0:
                query = query.filter_by(job_id=job_id).options(joinedload(Response.user))
            elif user_id > 0:
                query = query.filter_by(user_id=user_id).options(joinedload(Response.job))

            res = await session.execute(query)
            responses_from_db = res.scalars().all()

        if job_id > 0:
            with_user = True
            with_job = False
        else:
            with_user = False
            with_job = True
        responses_model = []
        for response in responses_from_db:
            model = self.__to_response_model(
                response_from_db=response, with_user=with_user, with_job=with_job
            )
            responses_model.append(model)

        return responses_model

    async def update(
        self, response_id: int, user_id: int, response_update_dto: ResponseUpdateSchema
    ) -> ResponseModel:
        async with self.session() as session:

            update_data = {
                key: value for key, value in response_update_dto.dict().items() if value is not None
            }
            query = (
                update(Response)
                .filter_by(id=response_id, user_id=user_id)
                .values(**update_data)
                .returning(Response)
            )
            result = await session.execute(query)
            updated_response = result.scalars().first()
            if not updated_response:
                raise ValueError("Отклик не найден")

        new_response = self.__to_response_model(updated_response, with_user=False, with_job=False)
        return new_response

    async def delete(self, response_id: int, user_id: int) -> ShortResponseModel:
        async with self.session() as session:
            query = (
                delete(Response).filter_by(id=response_id, user_id=user_id).returning(Response.id)
            )
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if not response_from_db:
                raise ValueError("Отклик не найден")

        return ShortResponseModel(id=response_id)

    @staticmethod
    def __to_response_model(
        response_from_db: Response, with_user: bool = False, with_job: bool = False
    ) -> ResponseModel | None:
        if not response_from_db:
            return None

        response_model = ResponseModel(
            id=response_from_db.id, message=response_from_db.message, user=None, job=None
        )
        if with_user:
            user = UserModel(
                id=response_from_db.id,
                name=response_from_db.user.name,
                email=response_from_db.user.email,
                is_company=response_from_db.user.is_company,
            )
            response_model.user = user
        if with_job:
            job = JobModel(
                id=response_from_db.job.id,
                title=response_from_db.job.title,
                description=response_from_db.job.description,
                salary_from=response_from_db.job.salary_from,
                salary_to=response_from_db.job.salary_to,
                is_active=response_from_db.job.is_active,
            )
            response_model.job = job

        return response_model
