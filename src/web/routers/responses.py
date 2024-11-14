from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories.job_repository import JobRepository
from repositories.response_repository import ResponseRepository
from services.response_service import ResponseService
from web.schemas.pagination import PaginationSchema
from web.schemas.response import ResponseSchema, ResponseUpdateSchema

responses_router = APIRouter(prefix="/responses", tags=["responses"])


@responses_router.get("")
@inject
async def get_response_by_user_id(
    pagination: PaginationSchema = Depends(),
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[ResponseSchema]:
    return await ResponseService(response_repository).get_response_list(
        limit=pagination.limit,
        skip=pagination.skip,
        current_user=current_user,
        job_repository=job_repository,
    )


@responses_router.get("/job_id")
@inject
async def get_responses_by_job_id(
    job_id: int,
    pagination: PaginationSchema = Depends(),
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[ResponseSchema]:
    return await ResponseService(response_repository).get_response_list(
        limit=pagination.limit,
        skip=pagination.skip,
        current_user=current_user,
        job_repository=job_repository,
        job_id=job_id,
    )


@responses_router.get("/response_id")
@inject
async def get_response_by_id(
    response_id: int,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseSchema | None:
    return await ResponseService(response_repository).get_response(
        response_id=response_id, current_user=current_user
    )


@responses_router.post("/job_id")
@inject
async def response_job(
    job_id: int,
    response_data: ResponseUpdateSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseSchema:
    return await ResponseService(response_repository).create_response(
        job_id=job_id,
        current_user=current_user,
        response_to_create=response_data,
    )


@responses_router.patch("/response_id")
@inject
async def update_response(
    response_id: int,
    response_data: ResponseUpdateSchema,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseSchema | None:
    return await ResponseService(response_repository).update_response(
        response_id=response_id,
        current_user=current_user,
        response_to_update=response_data,
    )


@responses_router.delete("/response_id")
@inject
async def delete_response(
    response_id: int,
    current_user: User = Depends(get_current_user),
    response_repository: ResponseRepository = Depends(
        Provide[RepositoriesContainer.response_repository]
    ),
) -> ResponseSchema | None:
    return await ResponseService(response_repository).delete_response(
        response_id=response_id, current_user=current_user
    )
