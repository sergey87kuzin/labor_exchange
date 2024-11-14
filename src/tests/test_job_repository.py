from decimal import Decimal

from storage.sqlalchemy.tables import Job, User
from tools.fixtures.jobs import JobFactory
from tools.fixtures.users import UserFactory
from web.schemas import JobCreateSchema, JobUpdateSchema
from web.schemas.filter import FilterSchema


async def create_user_and_job(sa_session) -> tuple[User, Job]:
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        job = JobFactory.build()
        job.user_id = user.id
        session.add(job)
        await session.flush()
    return user, job


def job_assertion(current_job: Job, expected_job: Job, user_id: int) -> None:
    assert current_job.id == expected_job.id
    assert current_job.title == expected_job.title
    assert current_job.description == expected_job.description
    assert current_job.salary_from == expected_job.salary_from
    assert current_job.salary_to == expected_job.salary_to
    assert current_job.is_active == expected_job.is_active
    assert current_job.created_at == expected_job.created_at
    assert current_job.user.id == user_id


async def test_get_all(job_repository, sa_session):
    user, job = await create_user_and_job(sa_session)

    job_filter = FilterSchema(company_id=user.id)
    all_jobs = await job_repository.retrieve_many(job_filter)
    assert all_jobs
    assert len(all_jobs) == 1, "Kомпания не видит собственные вакансии"

    job_filter.company_id = None
    all_candidate_jobs = await job_repository.retrieve_many(job_filter)
    assert all_candidate_jobs
    assert len(all_candidate_jobs) == 1, "Пользователь не видит вакансии"

    for jobs in [all_jobs, all_candidate_jobs]:
        assert jobs
        job_from_repo = jobs[0]
        job_assertion(job_from_repo, job, user.id)


async def test_get_by_id(job_repository, sa_session):
    user, job = await create_user_and_job(sa_session)

    current_job = await job_repository.retrieve(user_id=user.id)
    current_candidate_jobs = await job_repository.retrieve()
    for job in [current_job, current_candidate_jobs]:
        assert job is not None
        job_assertion(job, job, user.id)


async def test_create(job_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)

    job = JobCreateSchema(
        title="Test Job Title",
        description="Test Job Description",
        salary_from=Decimal("10000.01"),
        salary_to=Decimal("100000.01"),
        is_active=True,
        user_id=user.id,
    )

    new_job = await job_repository.create(job_to_create=job)
    assert new_job is not None
    assert new_job.title == "Test Job Title"
    assert new_job.salary_to == Decimal("100000.01")


async def test_update(job_repository, sa_session):
    user, job = await create_user_and_job(sa_session)

    job_to_update = JobUpdateSchema(
        title="updated_title",
        salary_from=Decimal("10000.01"),
        salary_to=Decimal("100000.01"),
    )
    updated_job = await job_repository.update(
        job_id=job.id, user_id=user.id, job_update_dto=job_to_update
    )
    assert job.id == updated_job.id
    assert updated_job.title == "updated_title"
    assert updated_job.salary_to == Decimal("100000.01")
    assert updated_job.salary_from == Decimal("10000.01")


async def test_update_job_by_other_user(job_repository, sa_session):
    user, job = await create_user_and_job(sa_session)
    async with sa_session() as session:
        wrong_user = UserFactory.build()
        session.add(wrong_user)

    job_to_update = JobUpdateSchema(
        title="updated_title",
        salary_from=Decimal("10000.01"),
        salary_to=Decimal("100000.01"),
    )
    updated_job = await job_repository.update(
        job_id=job.id, user_id=wrong_user.id, job_update_dto=job_to_update
    )
    assert not updated_job


async def test_delete(job_repository, sa_session):
    user, job = await create_user_and_job(sa_session)

    await job_repository.delete(job_id=job.id, user_id=user.id)
    deleted_job = await job_repository.retrieve(id=job.id)
    assert not deleted_job
