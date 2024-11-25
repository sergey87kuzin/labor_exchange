from http import HTTPStatus

import pytest

from tools.security import create_token
from web.schemas import UserCreateSchema, UserUpdateSchema


@pytest.mark.asyncio
async def test_create_user_request(client_app):
    user_create_dto = UserCreateSchema(
        name="some_name",
        email="some_email@example.com",
        password="some_password",
        password2="some_password",
        is_company=True,
    )
    user_create_url = "/users"
    resp = client_app.post(user_create_url, content=user_create_dto.model_dump_json())
    assert resp.status_code == HTTPStatus.OK
    token = create_token({"sub": user_create_dto.email})
    client_app.delete("/users", headers={"Authorization": f"Bearer {token}"})


@pytest.mark.asyncio
async def test_update_user_request(create_users, client_app):
    candidate_token, company_token = create_users
    user_update_dto = UserUpdateSchema(
        name="updated_name",
    )
    user_update_url = "/users"
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.patch(
            user_update_url,
            content=user_update_dto.model_dump_json(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status


@pytest.mark.asyncio
async def test_delete_user_request(create_users, client_app):
    candidate_token, company_token = create_users
    user_delete_url = "/users"
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.delete(user_delete_url, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status


@pytest.mark.asyncio
async def test_get_me_request(create_users, client_app):
    candidate_token, company_token = create_users
    user_me_url = "/users/me"
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.get(user_me_url, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status


@pytest.mark.asyncio
async def test_retrieve_user_request(create_users, client_app):
    candidate_token, company_token = create_users
    user_create_dto = UserCreateSchema(
        name="some_name",
        email="some_email@example.com",
        password="some_password",
        password2="some_password",
        is_company=True,
    )
    user_create_url = "/users"
    resp = client_app.post(user_create_url, content=user_create_dto.model_dump_json())
    user_id = resp.json()["id"]
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status
    token = create_token({"sub": user_create_dto.email})
    client_app.delete("/users", headers={"Authorization": f"Bearer {token}"})


@pytest.mark.asyncio
async def test_users_retrieve_request(create_users, client_app):
    candidate_token, company_token = create_users
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.get("/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == status
