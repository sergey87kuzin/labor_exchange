from dataclasses import asdict
from datetime import datetime
from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import Job as ShortJobModel
from models import User
from repositories.job_repository import JobRepository
from web.schemas.job import JobCreateSchema, JobSchema, JobUpdateSchema

jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])


@jobs_router.get("")
@inject
async def get_all_jobs(
    limit: int = 100,
    skip: int = 0,
    salary_from: int = None,
    salary_to: int = None,
    created_at: datetime = None,
    user_id: int = None,
    title: str = None,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> list[JobSchema]:
    kwargs = {}
    if salary_from:
        kwargs["salary_from"] = salary_from
    if salary_to:
        kwargs["salary_to"] = salary_to
    if created_at and created_at < datetime.now():
        kwargs["created_at"] = created_at
    if user_id:
        kwargs["user_id"] = user_id
    if title:
        kwargs["title"] = title
    # компания может видеть только свои вакансии
    if current_user and current_user.is_company:
        kwargs["user_id"] = current_user.id
    jobs_from_db = await job_repository.retrieve_many(limit=limit, skip=skip, **kwargs)
    return [JobSchema(**asdict(job)) for job in jobs_from_db]


@jobs_router.get("/job_id")
@inject
async def get_job_by_id(
    job_id: int,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema:
    kwargs = {"id": job_id}
    # компания может видеть только свои вакансии
    if current_user and current_user.is_company:
        kwargs["user_id"] = current_user.id
    try:
        job_model = await job_repository.retrieve(**kwargs)
        return JobSchema(**asdict(job_model))
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Вакансия не найдена",
        )


@jobs_router.post("")
@inject
async def create_job(
    job_creation_data: JobCreateSchema,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
):
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
    try:
        job_model = await job_repository.create(job_creation_data)
        return JobSchema(**asdict(job_model))
    except ValueError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=e.args[0],
        )
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Ошибка создания вакансии",
        )


@jobs_router.patch("/job_id")
@inject
async def update_job(
    job_id: int,
    job_update_data: JobUpdateSchema,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> JobSchema:
    if not current_user or not current_user.is_company:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Редактировать вакансии может только компания"
        )
    try:
        job = await job_repository.update(job_id, current_user.id, job_update_data)
        return JobSchema(**asdict(job))
    except IntegrityError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Ошибка изменения вакансии")
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Вакансия не найдена или открыта другой компанией",
        )


@jobs_router.delete("/job_id")
@inject
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    job_repository: JobRepository = Depends(Provide[RepositoriesContainer.job_repository]),
) -> ShortJobModel:
    if not current_user or not current_user.is_company:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Удалять вакансии могут только компании"
        )
    try:
        job = await job_repository.delete(job_id, user_id=current_user.id)
        return ShortJobModel(**asdict(job))
    except ValueError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Вакансия для удаления не найдена"
        )
