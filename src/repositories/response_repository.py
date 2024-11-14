from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session, joinedload

from interfaces import IRepositoryAsync
from models import ResponseWithUserAndJob as ResponseModel
from storage.sqlalchemy.tables import Response
from tools.to_model import ToModel
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema


class ResponseRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, response_to_create: ResponseCreateSchema) -> ResponseModel:
        async with self.session() as session:

            response = Response(**response_to_create.dict())

            session.add(response)
            await session.commit()

        return ToModel().to_response_model(
            response_from_db=response, with_user=False, with_job=False
        )

    async def retrieve(
        self, response_id: int, user_id: int, is_company: bool = False
    ) -> ResponseModel | None:
        async with self.session() as session:
            query = (
                select(Response)
                .filter_by(id=response_id)
                .options(joinedload(Response.user))
                .options(joinedload(Response.job))
                .limit(1)
            )

            res = await session.execute(query)
            response_from_db = res.scalars().first()
        if not response_from_db:
            return None
        return ToModel().to_response_model(
            response_from_db=response_from_db, with_user=True, with_job=True
        )

    async def retrieve_many(
        self, limit: int = 100, skip: int = 0, job_id: int = 0, user_id: int = 0
    ) -> list[ResponseModel]:
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
            model = ToModel().to_response_model(
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

        return ToModel().to_response_model(
            response_from_db=updated_response, with_user=False, with_job=False
        )

    async def delete(self, response_id: int, user_id: int) -> ResponseModel | None:
        async with self.session() as session:
            query = delete(Response).filter_by(id=response_id, user_id=user_id).returning(Response)
            res = await session.execute(query)
            response_from_db = res.scalars().first()

            if not response_from_db:
                return None

        return ToModel().to_response_model(
            response_from_db=response_from_db, with_user=False, with_job=False
        )
