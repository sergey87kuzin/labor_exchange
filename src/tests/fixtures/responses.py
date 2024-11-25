import pytest_asyncio

from tools.factories.jobs import JobFactory
from tools.factories.responses import ResponseFactory
from tools.factories.users import UserFactory
from web.schemas import ResponseUpdateSchema


@pytest_asyncio.fixture(scope="function")
async def create_users_job_and_response(sa_session):
    async def creation(with_response=True):
        async with sa_session() as session:
            company = UserFactory.build(is_company=True)
            session.add(company)
            candidate = UserFactory.build(is_company=False)
            session.add(candidate)
            job = JobFactory.build()
            job.user_id = company.id
            session.add(job)
            response = ResponseFactory.build()
            if with_response:
                response.user_id = candidate.id
                response.job_id = job.id
                session.add(response)
            await session.flush()
        return company, candidate, job, response

    return creation


@pytest_asyncio.fixture
async def create_response(create_job, client_app):
    """Создание 2 пользователей, вакансии и отклика в бд.
    Возвращает токены пользователей, вакансию, отклик"""
    candidate_token, company_token, job = create_job
    payload = ResponseUpdateSchema(message="some_message")
    response_create_url = f"responses/{job.get('id')}"
    resp = client_app.post(
        url=response_create_url,
        content=payload.model_dump_json(),
        headers={"Authorization": f"Bearer {candidate_token}"},
    )
    return candidate_token, company_token, job, resp.json()
