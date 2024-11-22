import pytest
from fastapi import HTTPException

from services.response_service import ResponseService
from tools.fixtures.users import UserFactory
from web.schemas import ResponseUpdateSchema


def assert_response(new_response, existing_response):
    assert new_response.message == existing_response.message


async def test_response_service_fail_creation(
    response_repository, create_two_companies_candidate_and_job
):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job

    response_creation_data = ResponseUpdateSchema(message="first_response_message")
    with pytest.raises(HTTPException) as e_info:
        await ResponseService(response_repository).create_object(
            job.id, wrong_company, response_creation_data
        )
    assert e_info.value.detail == "Откликаться на вакансии могут только соискатели"


async def test_response_service_success_creation(
    response_repository, create_two_companies_candidate_and_job
):
    right_company, wrong_company, candidate, job = create_two_companies_candidate_and_job

    response_creation_data = ResponseUpdateSchema(message="first_response_message")
    created_response = await ResponseService(response_repository).create_object(
        job_id=job.id, current_user=candidate, response_to_create=response_creation_data
    )
    assert created_response.message == response_creation_data.message
    response_from_db = await response_repository.retrieve(response_id=created_response.id)
    assert response_from_db.message == response_creation_data.message
    assert response_from_db.user.id == candidate.id
    assert response_from_db.job.id == job.id


async def test_response_service_failed_update(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)

    response_update_schema = ResponseUpdateSchema(
        message="new_response_message",
    )
    updated_response = await ResponseService(response_repository).update_object(
        response.id, company, response_update_schema
    )
    assert not updated_response
    response_from_db = await response_repository.retrieve(response_id=response.id)
    assert response_from_db.message == response.message


async def test_response_service_success_update(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)

    response_update_schema = ResponseUpdateSchema(
        message="new_response_message",
    )
    updated_response = await ResponseService(response_repository).update_object(
        response.id, candidate, response_update_schema
    )
    assert updated_response.message == response_update_schema.message
    response_from_db = await response_repository.retrieve(response_id=response.id)
    assert response_from_db.message == response_update_schema.message
    assert response_from_db.user.id == candidate.id
    assert response_from_db.job.id == job.id


async def test_response_service_failed_retrieve(
    response_repository, create_users_job_and_response, sa_session
):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()
    company, candidate, job, response = await create_users_job_and_response(with_response=True)
    result = await ResponseService(response_repository).retrieve_object(
        response_id=response.id,
        current_user=user,
    )
    assert not result


async def test_response_service_success_retrieve(
    response_repository,
    create_users_job_and_response,
):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)
    for user in (company, candidate):
        response_from_db = await ResponseService(response_repository).retrieve_object(
            response_id=response.id,
            current_user=user,
        )
        assert response_from_db.message == response.message
        assert response_from_db.user.id == candidate.id
        assert response_from_db.job.id == job.id


async def test_response_service_failed_retrieve_many(
    response_repository, job_repository, create_users_job_and_response, sa_session
):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)
    async with sa_session() as session:
        new_company = UserFactory.build(is_company=True)
        session.add(new_company)
        await session.flush()
    for job_id, user, error_text in (
        (None, new_company, "Пользовательские отклики невозможны для компаний"),
        (job.id, candidate, "Клиент не может посмотреть отклики на вакансию"),
        (job.id, new_company, "Можно просматривать только свои отклики"),
    ):
        with pytest.raises(HTTPException) as e_info:
            await ResponseService(response_repository).retrieve_many_objects(
                limit=5,
                skip=0,
                current_user=user,
                job_id=job_id,
                job_repository=job_repository,
            )
        assert e_info.value.detail == error_text


async def test_response_service_success_retrieve_many(
    response_repository,
    job_repository,
    create_users_job_and_response,
):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)

    responses_from_db = await ResponseService(response_repository).retrieve_many_objects(
        limit=5,
        skip=0,
        current_user=company,
        job_id=job.id,
        job_repository=job_repository,
    )
    assert len(responses_from_db) == 1
    response_from_db = responses_from_db[0]
    assert response_from_db.message == response.message
    assert response_from_db.user.id == candidate.id


async def test_response_service_failed_delete(
    response_repository, create_users_job_and_response, sa_session
):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)
    async with sa_session() as session:
        new_candidate = UserFactory.build(is_company=False)
        session.add(new_candidate)
        await session.flush()
    with pytest.raises(HTTPException) as e_info:
        await ResponseService(response_repository).delete_object(response.id, company)
    assert e_info.value.detail == "Удалить отклик может только соискатель"
    deleted_response = await ResponseService(response_repository).delete_object(
        response.id, new_candidate
    )
    assert not deleted_response


async def test_job_service_success_delete(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response(with_response=True)

    deleted_response = await ResponseService(response_repository).delete_object(
        response.id, candidate
    )
    assert deleted_response.id == response.id

    response_from_db = await response_repository.retrieve(response_id=deleted_response.id)
    assert not response_from_db
