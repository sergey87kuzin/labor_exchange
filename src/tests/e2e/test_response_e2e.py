from http import HTTPStatus

import pytest

from tests.fixtures import create_users  # noqa
from web.schemas import ResponseUpdateSchema


@pytest.mark.asyncio
async def test_response_create_request(create_job, client_app):
    candidate_token, company_token, job = create_job
    payload = ResponseUpdateSchema(message="some_message")
    response_create_url = f"/responses/{job.get('id')}"
    for headers, status in (
        ({}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.FORBIDDEN),
    ):
        response = client_app.post(
            response_create_url,
            content=payload.model_dump_json(),
            headers=headers,
        )
        assert response.status_code == status


@pytest.mark.asyncio
async def test_response_update_request(create_response, client_app):
    candidate_token, company_token, job, response = create_response
    payload = ResponseUpdateSchema(message="some_message")
    response_create_url = f"/responses/{response.get('id')}"
    for headers, status in (
        ({}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.OK),
    ):
        response = client_app.patch(
            response_create_url,
            content=payload.model_dump_json(),
            headers=headers,
        )
        assert response.status_code == status


@pytest.mark.asyncio
async def test_response_delete_request(create_response, client_app):
    candidate_token, company_token, job, response = create_response
    response_create_url = f"/responses/{response.get('id')}"
    for headers, status in (
        ({}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.OK),
    ):
        response = client_app.delete(
            response_create_url,
            headers=headers,
        )
        assert response.status_code == status


@pytest.mark.asyncio
async def test_response_retrieve_request(create_response, client_app):
    candidate_token, company_token, job, response = create_response
    response_retrieve_url = f"/responses/{response.get('id')}"
    for headers, status in (
        ({}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.OK),
    ):
        response = client_app.get(
            response_retrieve_url,
            headers=headers,
        )
        assert response.status_code == status


@pytest.mark.asyncio
async def test_response_retrieve_job_request(create_response, client_app):
    candidate_token, company_token, job, response = create_response
    response_retrieve_url = f"/responses/job/{job.get('id')}"
    for headers, status in (
        ({}, HTTPStatus.FORBIDDEN),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.FORBIDDEN),
    ):
        response = client_app.get(
            response_retrieve_url,
            headers=headers,
        )
        assert response.status_code == status
