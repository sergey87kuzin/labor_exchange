from decimal import Decimal
from http import HTTPStatus

from web.schemas import JobCreateSchema, JobUpdateSchema


async def test_job_create_request(create_users, client_app):
    """Тест запроса на эндпоинт создания вакансии"""
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
    for token, status in [
        (candidate_token, HTTPStatus.FORBIDDEN),
        (company_token, HTTPStatus.OK),
    ]:
        resp = client_app.post(
            url=jobs_create_url,
            content=payload.model_dump_json(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status


async def test_job_update_request(create_job, client_app):
    """Тест запроса на эндпоинт изменения вакансии"""
    candidate_token, company_token, job = create_job
    payload = JobUpdateSchema(
        title="updated title",
        description="updated description",
        is_active=True,
        salary_from=Decimal("10000.00"),
        salary_to=Decimal("100000.00"),
    )
    job_update_url = "/jobs/{}".format(job["id"])
    for token, status in (
        (candidate_token, HTTPStatus.FORBIDDEN),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.patch(
            job_update_url,
            content=payload.model_dump_json(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status


async def test_job_delete_request(create_job, client_app):
    """Тест запроса на эндпоинт удаления вакансии"""
    candidate_token, company_token, job = create_job
    job_update_url = "/jobs/{}".format(job["id"])
    for token, status in (
        (candidate_token, HTTPStatus.FORBIDDEN),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.delete(
            job_update_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status


async def test_get_job_request(create_job, client_app):
    """Тест запроса на эндпоинт получения вакансии"""
    candidate_token, company_token, job = create_job
    get_job_url = "/jobs/{}".format(job["id"])
    for token, status in (
        (candidate_token, HTTPStatus.OK),
        (company_token, HTTPStatus.OK),
    ):
        resp = client_app.get(
            get_job_url,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status


async def test_get_all_jobs_request(create_job, client_app):
    """Тест запроса на эндпоинт получения списка вакансий"""
    candidate_token, company_token, job = create_job
    get_job_url = "/jobs"
    for headers, status in (
        ({}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {candidate_token}"}, HTTPStatus.OK),
        ({"Authorization": f"Bearer {company_token}"}, HTTPStatus.OK),
    ):
        resp = client_app.get(
            get_job_url,
            headers=headers,
        )
        assert resp.status_code == status
