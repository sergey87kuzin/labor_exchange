import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import DBSettings
from main import app
from repositories import JobRepository, ResponseRepository, UserRepository
from storage.sqlalchemy.client import SqlAlchemyAsync
from tests.fixtures import (  # noqa
    create_candidate_and_company,
    create_job,
    create_response,
    create_two_companies_candidate_and_job,
    create_user_and_job,
    create_users,
    create_users_job_and_response,
)
from tools.factories.jobs import JobFactory
from tools.factories.responses import ResponseFactory
from tools.factories.users import UserFactory

env_file_name = ".env." + os.environ.get("STAGE", "test")
env_file_path = Path(__file__).parent.parent.resolve() / env_file_name
settings = DBSettings(_env_file=env_file_path)


@pytest.fixture()
def client_app():
    app.container.db.override(
        providers.Factory(
            SqlAlchemyAsync,
            pg_settings=settings,
        ),
    )
    client = TestClient(app)
    return client


@pytest_asyncio.fixture(scope="function")
async def sa_session():
    engine = create_async_engine(str(settings.pg_async_dsn))
    connection = await engine.connect()
    trans = await connection.begin()

    Session = sessionmaker(connection, expire_on_commit=False, class_=AsyncSession)  # noqa
    session = Session()

    deletion = session.delete

    async def mock_delete(instance):
        insp = inspect(instance)
        if not insp.persistent:
            session.expunge(instance)
        else:
            await deletion(instance)

        return await asyncio.sleep(0)

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    @asynccontextmanager
    async def db():
        yield session

    session.commit = MagicMock(side_effect=session.flush)
    session.delete = MagicMock(side_effect=mock_delete)

    try:
        yield db
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def user_repository(sa_session):
    repository = UserRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function")
async def job_repository(sa_session):
    repository = JobRepository(session=sa_session)
    yield repository


@pytest_asyncio.fixture(scope="function")
async def response_repository(sa_session):
    repository = ResponseRepository(session=sa_session)
    yield repository


# регистрация фабрик
@pytest_asyncio.fixture(scope="function", autouse=True)
def setup_factories(sa_session: AsyncSession) -> None:
    UserFactory.session = sa_session
    JobFactory.session = sa_session
    ResponseFactory.session = sa_session
