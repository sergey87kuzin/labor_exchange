from storage.sqlalchemy.tables import Job, Response, User
from tools.fixtures.jobs import JobFactory
from tools.fixtures.responses import ResponseFactory
from tools.fixtures.users import UserFactory


async def create_users_job_and_response(sa_session) -> tuple[User, User, Job, Response]:
    async with sa_session() as session:
        company = UserFactory.build(is_company=True)
        session.add(company)
        candidate = UserFactory.build(is_company=False)
        session.add(candidate)
        job = JobFactory.build()
        job.user_id = company.id
        session.add(job)
        response = ResponseFactory.build()
        response.user_id = candidate.id
        response.job_id = job.id
        session.add(response)
        await session.flush()
    return company, candidate, job, response


async def test_get_all(response_repository, sa_session):
    company, candidate, job, response = await create_users_job_and_response(sa_session)

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
        assert response_from_repo.job_id == job.id
        assert response_from_repo.message == response.message


# async def test_get_by_id(job_repository, sa_session):
#     user, job = await create_user_and_job(sa_session)
#
#     current_job = await job_repository.retrieve(user_id=user.id)
#     current_candidate_jobs = await job_repository.retrieve()
#     for job in [current_job, current_candidate_jobs]:
#         assert job is not None
#         job_assertion(job, job, user.id)
#
#
# async def test_create(job_repository, sa_session):
#     async with sa_session() as session:
#         user = UserFactory.build(is_company=True)
#         session.add(user)
#
#     job = JobCreateSchema(
#         title="Test Job Title",
#         description="Test Job Description",
#         salary_from=Decimal("10000.01"),
#         salary_to=Decimal("100000.01"),
#         is_active=True,
#         user_id=user.id,
#     )
#
#     new_job = await job_repository.create(job_to_create=job)
#     assert new_job is not None
#     assert new_job.title == "Test Job Title"
#     assert new_job.salary_to == Decimal("100000.01")
#
#
# async def test_update(job_repository, sa_session):
#     user, job = await create_user_and_job(sa_session)
#
#     job_to_update = JobUpdateSchema(
#         title="updated_title",
#         salary_from=Decimal("10000.01"),
#         salary_to=Decimal("100000.01"),
#     )
#     updated_job = await job_repository.update(
#     job_id=job.id, user_id=user.id, job_update_dto=job_to_update)
#     assert job.id == updated_job.id
#     assert updated_job.title == "updated_title"
#     assert updated_job.salary_to == Decimal("100000.01")
#     assert updated_job.salary_from == Decimal("10000.01")
#
#
# async def test_update_job_by_other_user(job_repository, sa_session):
#     user, job = await create_user_and_job(sa_session)
#     async with sa_session() as session:
#         wrong_user = UserFactory.build()
#         session.add(wrong_user)
#
#     job_to_update = JobUpdateSchema(
#         title="updated_title",
#         salary_from=Decimal("10000.01"),
#         salary_to=Decimal("100000.01"),
#     )
#     with pytest.raises(ValueError):
#         await job_repository.update(
#         job_id=job.id, user_id=wrong_user.id, job_update_dto=job_to_update)
#
#
# async def test_delete(job_repository, sa_session):
#     user, job = await create_user_and_job(sa_session)
#
#     await job_repository.delete(job_id=job.id, user_id=user.id)
#     with pytest.raises(ValueError):
#         await job_repository.retrieve(id=job.id)
