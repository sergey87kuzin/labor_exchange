from decimal import Decimal

import pytest
from fastapi import HTTPException

from services.job_service import JobService
from tools.factories.users import UserFactory
from tools.security import create_token
from web.schemas import JobCreateSchema, JobUpdateSchema
from web.schemas.filter import FilterSchema
from web.schemas.pagination import PaginationSchema


def assert_job(new_job, existing_job):
    assert new_job.title == existing_job.title
    assert new_job.salary_from == existing_job.salary_from
    assert new_job.salary_to == existing_job.salary_to
    assert new_job.description == existing_job.description
    assert new_job.is_active == existing_job.is_active


@pytest.mark.asyncio
async def test_job_service_fail_creation(job_repository, create_candidate_and_company):
    candidate, company = create_candidate_and_company

    job_creation_data = JobCreateSchema(
        salary_from=Decimal("100.00"),
        salary_to=Decimal("100000.00"),
        title="first_job_title",
        user_id=candidate.id,
        description="first_job_description",
        is_active=True,
    )
    with pytest.raises(HTTPException) as e_info:
        await JobService(job_repository).create_object(candidate, job_creation_data)
    assert e_info.value.detail == "Только компания может создавать вакансию"
    with pytest.raises(HTTPException) as e_info:
        await JobService(job_repository).create_object(company, job_creation_data)
    assert e_info.value.detail == "Можно создать вакансию только от имени своей компании"


@pytest.mark.asyncio
async def test_job_service_success_creation(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        await session.flush()

    job_creation_data = JobCreateSchema(
        salary_from=Decimal("100.00"),
        salary_to=Decimal("100000.00"),
        title="first_job_title",
        user_id=user.id,
        description="first_job_description",
        is_active=True,
    )
    created_job = await JobService(job_repository).create_object(user, job_creation_data)
    assert_job(created_job, job_creation_data)
    job_from_db = await job_repository.retrieve(id=created_job.id)
    assert_job(job_from_db, job_creation_data)


@pytest.mark.asyncio
async def test_job_service_failed_update(job_repository, create_two_companies_candidate_and_job):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job

    job_update_schema = JobUpdateSchema(
        salary_from=Decimal("100.00"),
        salary_to=Decimal("100000.00"),
        title="first_job_title",
        description="first_job_description",
        is_active=True,
    )
    with pytest.raises(HTTPException) as e_info:
        await JobService(job_repository).update_object(job.id, candidate, job_update_schema)
    assert e_info.value.detail == "Редактировать вакансии может только компания"
    updated_job = await JobService(job_repository).update_object(
        job.id, wrong_company, job_update_schema
    )
    assert not updated_job
    job_from_db = await job_repository.retrieve(id=job.id)
    assert_job(job_from_db, job)


@pytest.mark.asyncio
async def test_job_service_success_update(job_repository, create_user_and_job):
    user, job = create_user_and_job

    job_update_schema = JobUpdateSchema(
        salary_from=Decimal("100.00"),
        salary_to=Decimal("100000.00"),
        title="first_job_title",
        description="first_job_description",
        is_active=True,
    )
    updated_job = await JobService(job_repository).update_object(job.id, user, job_update_schema)
    assert updated_job.id == job.id
    assert_job(updated_job, job)
    job_from_db = await job_repository.retrieve(id=updated_job.id)
    assert_job(job_from_db, updated_job)


@pytest.mark.asyncio
async def test_job_service_failed_retrieve(
    job_repository, user_repository, create_two_companies_candidate_and_job
):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job
    wrong_company_token = create_token({"sub": wrong_company.email})
    result = await JobService(job_repository).retrieve_object(
        job_id=job.id, user_repository=user_repository, token=wrong_company_token
    )
    assert not result


@pytest.mark.asyncio
async def test_job_service_success_retrieve(
    job_repository, user_repository, create_two_companies_candidate_and_job
):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job
    company_token = create_token({"sub": right_company.email})
    candidate_token = create_token({"sub": candidate.email})
    retrieve_variants = (None, candidate_token, company_token)
    for token in retrieve_variants:
        result = await JobService(job_repository).retrieve_object(
            job_id=job.id, user_repository=user_repository, token=token
        )
        assert_job(result, job)


@pytest.mark.asyncio
async def test_job_service_retrieve_many(
    job_repository, user_repository, create_two_companies_candidate_and_job
):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job
    company_token = create_token({"sub": right_company.email})
    candidate_token = create_token({"sub": candidate.email})

    pagination = PaginationSchema(limit=5, skip=0)
    filter_schema = FilterSchema(company_id=right_company.id)
    for token in (None, candidate_token, company_token):
        jobs_from_db = await JobService(job_repository).retrieve_many_objects(
            pagination=pagination,
            jobs_filter=filter_schema,
            user_repository=user_repository,
            token=token,
        )
        assert len(jobs_from_db) == 1
        assert_job(jobs_from_db[0], job)


@pytest.mark.asyncio
async def test_job_service_failed_delete(job_repository, create_two_companies_candidate_and_job):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job

    deleted_job = await JobService(job_repository).delete_object(job.id, wrong_company)
    assert not deleted_job


@pytest.mark.asyncio
async def test_job_service_success_delete(job_repository, create_two_companies_candidate_and_job):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job

    deleted_job = await JobService(job_repository).delete_object(job.id, right_company)
    assert_job(deleted_job, job)

    job_from_db = await job_repository.retrieve(id=deleted_job.id)
    assert not job_from_db
