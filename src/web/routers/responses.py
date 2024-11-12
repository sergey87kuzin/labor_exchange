from dataclasses import asdict
from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import Response as ShortResponseModel
from models import ResponseWithUserAndJob as ResponseModel
from models import User
from repositories.job_repository import JobRepository
from repositories.response_repository import ResponseRepository
from web.schemas.response import ResponseCreateSchema, ResponseUpdateSchema

responses_router = APIRouter(prefix="/responses", tags=["responses"])


async def get_responses(
    limit: int, skip: int, repository: ResponseRepository, user_id: int = 0, job_id: int = 0
):
    try:
        response_models = await repository.retrieve_many(
            limit=limit, skip=skip, user_id=user_id, job_id=job_id
        )
        return [ResponseModel(**asdict(response)) for response in response_models]
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=e.args[0],
        )
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Ошибка получения откликов из базы"
        )


@responses_router.get("")
@inject
async def get_response_by_user_id(
    limit: int = 100,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> list[ResponseModel]:
    if not current_user or current_user.is_company:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Пользовательские отклики невозможны для компаний",
        )
    return await get_responses(
        limit=limit, skip=skip, repository=response_repository, user_id=current_user.id
    )


@responses_router.get("/job_id")
@inject
async def get_responses_by_job_id(
    job_id: int,
    limit: int = 100,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[ResponseModel]:
    if not current_user or not current_user.is_company:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Отклики на вакансию просмативает только компания",
        )
    try:
        await job_repository.retrieve(job_id=job_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=e.args[0],
        )
    return await get_responses(
        limit=limit, skip=skip, repository=response_repository, job_id=job_id
    )


@responses_router.get("/response_id")
@inject
async def get_response_by_id(
    response_id: int,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> list[ResponseModel]:
    try:
        return await response_repository.retrieve_by_user_id(
            response_id=response_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=e.args[0],
        )


@responses_router.post("/job_id")
@inject
async def response_job(
    job_id: int,
    response_data: ResponseCreateSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseModel:
    pass


@responses_router.patch("/response_id")
@inject
async def update_response(
    response_id: int,
    response_data: ResponseUpdateSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseModel:
    pass


@responses_router.delete("/response_id")
@inject
async def delete_response(
    response_id: int,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ShortResponseModel:
    pass
