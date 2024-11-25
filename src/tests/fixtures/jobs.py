from decimal import Decimal

import pytest_asyncio

from tools.factories.jobs import JobFactory
from tools.factories.users import UserFactory
from web.schemas import JobCreateSchema


@pytest_asyncio.fixture(scope="function")
async def create_user_and_job(sa_session):
    async with sa_session() as session:
        user = UserFactory.build(is_company=True)
        session.add(user)
        job = JobFactory.build()
        job.user_id = user.id
        session.add(job)
        await session.flush()
    return user, job


@pytest_asyncio.fixture(scope="function")
async def create_two_companies_candidate_and_job(sa_session):
    async with sa_session() as session:
        right_company = UserFactory.build(is_company=True)
        session.add(right_company)
        wrong_company = UserFactory.build(is_company=True)
        session.add(wrong_company)
        candidate = UserFactory.build(is_company=False)
        session.add(candidate)
        job = JobFactory.build()
        job.user_id = right_company.id
        session.add(job)
        await session.flush()
    return right_company, wrong_company, candidate, job


@pytest_asyncio.fixture
async def create_job(create_users, client_app):
    """Создание 2 пользователей и вакансии в бд. Возвращает токены пользователей и вакансию"""
    candidate_token, company_token = create_users
    payload = JobCreateSchema(
        user_id=None,
        title="some title",
        description="some description",
        is_active=True,
        salary_from=Decimal("10000.00"),
        salary_to=Decimal("100000.00"),
    )
    jobs_create_url = "/jobs"
    resp = client_app.post(
        url=jobs_create_url,
        content=payload.model_dump_json(),
        headers={"Authorization": f"Bearer {company_token}"},
    )
    return candidate_token, company_token, resp.json()
