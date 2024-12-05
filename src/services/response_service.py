from dataclasses import asdict
from http import HTTPStatus

from fastapi import HTTPException

from interfaces import IService
from models import User
from repositories.job_repository import JobRepository
from repositories.response_repository import ResponseRepository
from web.schemas import ResponseCreateSchema, ResponseSchema, ResponseUpdateSchema


class ResponseService(IService):
    def __init__(self, response_repository: ResponseRepository):
        self.response_repository = response_repository

    async def retrieve_object(self, response_id: int, current_user: User) -> ResponseSchema | None:
        response_from_db = await self.response_repository.retrieve(
            response_id=response_id, user_id=current_user.id, is_company=current_user.is_company
        )
        if not response_from_db:
            return None
        if current_user.is_company and response_from_db.job.user_id != current_user.id:
            return None
        if not current_user.is_company and response_from_db.user_id != current_user.id:
            return None
        return ResponseSchema(**asdict(response_from_db))

    async def retrieve_many_objects(
        self,
        limit: int,
        skip: int,
        current_user: User,
        job_repository: JobRepository,
        job_id: int = None,
    ) -> list[ResponseSchema]:
        if not job_id and current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Пользовательские отклики невозможны для компаний",
            )
        if job_id and not current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Клиент не может посмотреть отклики на вакансию",
            )
        if job_id:
            checked_job = await job_repository.retrieve(id=job_id, user_id=current_user.id)
            if not checked_job:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail="Можно просматривать только свои выкансии",
                )
            response_models = await self.response_repository.retrieve_many(
                limit=limit, skip=skip, job_id=job_id
            )
        else:
            response_models = await self.response_repository.retrieve_many(
                limit=limit, skip=skip, user_id=current_user.id
            )
        return [ResponseSchema(**asdict(response)) for response in response_models]

    async def create_object(
        self, job_id: int, current_user: User, response_to_create: ResponseUpdateSchema
    ) -> ResponseSchema | None:
        if current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Откликаться на вакансии могут только соискатели",
            )
        response_from_db = await self.response_repository.create(
            response_to_create=ResponseCreateSchema(
                message=response_to_create.message, job_id=job_id, user_id=current_user.id
            ),
        )
        if not response_from_db:
            return None
        return ResponseSchema(**asdict(response_from_db))

    async def update_object(
        self, response_id: int, current_user: User, response_to_update: ResponseUpdateSchema
    ) -> ResponseSchema | None:
        response_from_db = await self.response_repository.update(
            response_id=response_id, user_id=current_user.id, response_update_dto=response_to_update
        )
        if not response_from_db:
            return None
        return ResponseSchema(**asdict(response_from_db))

    async def delete_object(
        self,
        response_id: int,
        current_user: User,
    ) -> ResponseSchema | None:
        if current_user.is_company:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Удалить отклик может только соискатель",
            )
        response_from_db = await self.response_repository.delete(
            response_id=response_id, user_id=current_user.id
        )
        if not response_from_db:
            return None
        return ResponseSchema(**asdict(response_from_db))
