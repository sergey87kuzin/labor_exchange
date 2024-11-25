import pytest_asyncio

from tools.factories.users import UserFactory
from tools.security import create_token
from web.schemas import UserCreateSchema


@pytest_asyncio.fixture(scope="function")
async def create_candidate_and_company(sa_session):
    async with sa_session() as session:
        company = UserFactory.build(is_company=True)
        session.add(company)
        candidate = UserFactory.build(is_company=False)
        session.add(candidate)
        await session.flush()
    return candidate, company


@pytest_asyncio.fixture(scope="function")
async def create_users(client_app):
    """Создание двух пользователей в бд, соискателя и компании. Возвращает их токены"""
    candidate_data = UserFactory.build(is_company=False)
    company_data = UserFactory.build(is_company=True)
    candidate_dto = UserCreateSchema(
        name=candidate_data.name,
        email=candidate_data.email,
        password="some_password",
        password2="some_password",
        is_company=candidate_data.is_company,
    )
    company_dto = UserCreateSchema(
        name=company_data.name,
        email=company_data.email,
        password="some_password",
        password2="some_password",
        is_company=company_data.is_company,
    )
    user_create_url = "/users"
    client_app.post(user_create_url, content=candidate_dto.model_dump_json())
    client_app.post(user_create_url, content=company_dto.model_dump_json())
    candidate_token = create_token({"sub": candidate_data.email})
    company_token = create_token({"sub": company_data.email})
    yield candidate_token, company_token
    client_app.delete(user_create_url, headers={"Authorization": f"Bearer {candidate_token}"})
    client_app.delete(user_create_url, headers={"Authorization": f"Bearer {company_token}"})
