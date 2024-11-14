from web.schemas import ResponseCreateSchema, ResponseUpdateSchema


async def test_get_all(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response()

    all_job_responses = await response_repository.retrieve_many(job_id=job.id)
    assert all_job_responses
    assert len(all_job_responses) == 1, "Kомпания не видит отклики на собственные вакансии"

    all_candidate_responses = await response_repository.retrieve_many()
    assert all_candidate_responses
    assert len(all_candidate_responses) == 1, "Пользователь не видит свои отклики на вакансии"

    for jobs in [all_job_responses, all_candidate_responses]:
        assert jobs
        response_from_repo = jobs[0]
        assert response_from_repo.id == response.id
        assert response_from_repo.user_id == candidate.id
        assert response_from_repo.message == response.message


async def test_get_by_id(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response()

    current_response = await response_repository.retrieve(response_id=response.id)
    assert current_response is not None
    assert current_response.id == response.id
    assert current_response.user_id == candidate.id
    assert current_response.message == response.message


async def test_create(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response(with_response=False)

    response_to_create = ResponseCreateSchema(
        message="response_message",
        user_id=candidate.id,
        job_id=job.id,
    )

    new_response = await response_repository.create(response_to_create=response_to_create)
    assert new_response is not None
    assert new_response.message == "response_message"
    assert new_response.user_id == candidate.id


async def test_update(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response()

    response_to_update = ResponseUpdateSchema(message="updated_message")
    updated_response = await response_repository.update(
        response_id=response.id, user_id=candidate.id, response_update_dto=response_to_update
    )
    assert response.id == updated_response.id
    assert updated_response.message == "updated_message"
    assert updated_response.user_id == candidate.id

    response_from_db = await response_repository.retrieve(response_id=response.id)
    assert response_from_db.message == "updated_message", "Изменения не сохранились в бд"

    wrong_response = await response_repository.update(
        response_id=response.id, user_id=company.id, response_update_dto=response_to_update
    )
    assert not wrong_response, "Другим пользователям позволено редактировать отклик"


async def test_delete(response_repository, create_users_job_and_response):
    company, candidate, job, response = await create_users_job_and_response()

    wrong_response = await response_repository.delete(response_id=response.id, user_id=company.id)
    assert not wrong_response, "Другие пользователи могут удалять отзыв"

    right_response = await response_repository.delete(response_id=response.id, user_id=candidate.id)
    assert right_response
    assert right_response.id == response.id
    check_response = await response_repository.retrieve(response_id=response.id)
    assert not check_response
