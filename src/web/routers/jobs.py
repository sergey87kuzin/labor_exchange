from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from repositories.job_repository import JobRepository
from services.job_service import JobService
from tools.security import JWTBearer
from web.schemas.filter import FilterSchema
from web.schemas.job import JobCreateSchema, JobSchema, JobUpdateSchema
from web.schemas.pagination import PaginationSchema

jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])


@jobs_router.get("")
@inject
async def get_all_jobs(
    pagination: PaginationSchema = Depends(),
    jobs_filter: FilterSchema = Depends(),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    token: str = Depends(JWTBearer(auto_error=False)),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[JobSchema]:
    return await JobService(job_repository).jobs_list(
        pagination, jobs_filter, user_repository, token
    )


@jobs_router.get("/job_id")
@inject
async def get_job_by_id(
    job_id: int,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    token: str = Depends(JWTBearer(auto_error=False)),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema | None:
    return await JobService(job_repository).job_details(job_id, user_repository, token)


@jobs_router.post("")
@inject
async def create_job(
    job_creation_data: JobCreateSchema,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema:
    return await JobService(job_repository).create_job(current_user, job_creation_data)


@jobs_router.patch("/job_id")
@inject
async def update_job(
    job_id: int,
    job_update_data: JobUpdateSchema,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema | None:
    return await JobService(job_repository).job_update(
        job_id=job_id, current_user=current_user, job_update_data=job_update_data
    )


@jobs_router.delete("/job_id")
@inject
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema | None:
    return await JobService(job_repository).job_delete(job_id=job_id, current_user=current_user)
