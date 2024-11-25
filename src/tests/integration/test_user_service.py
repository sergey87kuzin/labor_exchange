import pytest
from fastapi import HTTPException

from services.user_service import UserService
from tools.factories.users import UserFactory
from tools.security import create_token
from web.schemas import UserCreateSchema, UserUpdateSchema


def assert_user(new_user, existing_user):
    assert new_user.email == existing_user.email
    assert new_user.name == existing_user.name
    assert new_user.is_company == existing_user.is_company


@pytest.mark.asyncio
async def test_user_service_fail_creation(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(email="already_exists@email.ru")
        session.add(user)
        await session.flush()

    user_create_dto = UserCreateSchema(
        name="some_name",
        email="already_exists@email.ru",
        password="some_password",
        password2="some_password",
        is_company=True,
    )
    with pytest.raises(HTTPException) as e_info:
        await UserService(user_repository).create_object(user_create_dto)
    assert e_info.value.detail == "Пользователь уже существует"


@pytest.mark.asyncio
async def test_user_service_success_creation(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(email="already_exists@email.ru")
        session.add(user)
        await session.flush()

    user_create_dto = UserCreateSchema(
        name="some_name",
        email="already_exists@email.ru",
        password="some_password",
        password2="some_password",
        is_company=True,
    )
    user_create_dto.email = "not_already_exists@email.ru"
    new_user = await UserService(user_repository).create_object(user_create_dto)
    assert_user(new_user, user_create_dto)
    user_from_db = await user_repository.retrieve(id=new_user.id)
    assert_user(user_from_db, new_user)


@pytest.mark.asyncio
async def test_user_service_failed_update(user_repository, create_candidate_and_company):
    candidate, company = create_candidate_and_company

    user_update_schema = UserUpdateSchema(name="some_name", email=candidate.email, is_company=True)
    with pytest.raises(HTTPException) as e_info:
        await UserService(user_repository).update_object(user_update_schema, company)
    assert e_info.value.detail == "Недостаточно прав"


@pytest.mark.asyncio
async def test_user_service_success_update(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build(email="user@email.ru")
        session.add(user)
        await session.flush()

    user_update_schema = UserUpdateSchema(name="some_name", email="user@email.ru", is_company=True)
    updated_user = await UserService(user_repository).update_object(user_update_schema, user)
    assert updated_user.id == user.id
    assert_user(updated_user, user)
    user_from_db = await user_repository.retrieve(id=updated_user.id)
    assert_user(user_from_db, updated_user)


@pytest.mark.asyncio
async def test_user_service_failed_retrieve(user_repository, sa_session):
    async with sa_session() as session:
        company = UserFactory.build(is_company=True)
        session.add(company)
        another_company = UserFactory.build(is_company=True)
        session.add(another_company)
        candidate = UserFactory.build(is_company=False)
        session.add(candidate)
        another_candidate = UserFactory.build(is_company=False)
        session.add(another_candidate)
        await session.flush()
    company_token = create_token({"sub": company.email})
    candidate_token = create_token({"sub": candidate.email})
    retrieve_variants = (
        (candidate.id, None),  # Незарегистрированный пользователь считается соискателем
        (another_company.id, company_token),  # Компания не видит другие компании
        (another_candidate.id, candidate_token),  # соискатель не видит других соискателей
    )
    for user_id, token in retrieve_variants:

        result = await UserService(user_repository).retrieve_object(user_id=user_id, token=token)
        assert not result


@pytest.mark.asyncio
async def test_user_service_success_retrieve(user_repository, create_candidate_and_company):
    candidate, company = create_candidate_and_company
    company_token = create_token({"sub": company.email})
    candidate_token = create_token({"sub": candidate.email})
    retrieve_variants = (
        (company.id, None, company),  # Незарегистрированный пользователь считается соискателем
        (company.id, candidate_token, company),  # Компания не видит другие компании
        (candidate.id, company_token, candidate),  # соискатель не видит других соискателей
    )
    for user_id, token, user in retrieve_variants:

        result = await UserService(user_repository).retrieve_object(user_id=user_id, token=token)
        assert_user(result, user)


@pytest.mark.asyncio
async def test_user_service_me(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    me = await UserService(user_repository).get_me(user)
    assert_user(me, user)


@pytest.mark.asyncio
async def test_user_service_retrieve_many(user_repository, create_candidate_and_company):
    candidate, company = create_candidate_and_company
    company_token = create_token({"sub": company.email})
    candidate_token = create_token({"sub": candidate.email})

    for token, user in (
        (None, company),
        (candidate_token, company),
        (company_token, candidate),
    ):
        users_from_db = await UserService(user_repository).retrieve_many_objects(
            limit=5, skip=0, token=token
        )
        assert len(users_from_db) == 1
        assert_user(users_from_db[0], user)


@pytest.mark.asyncio
async def test_user_service_delete(user_repository, sa_session):
    async with sa_session() as session:
        user = UserFactory.build()
        session.add(user)
        await session.flush()

    deleted_user = await UserService(user_repository).delete_object(user)
    assert_user(deleted_user, user)

    user_from_db = await user_repository.retrieve(id=user.id)
    assert not user_from_db
