from decimal import Decimal
from http import HTTPStatus

from tools.security import create_token
from web.schemas import JobCreateSchema


async def test_job_create_request(create_candidate_and_company, client_app):
    candidate, company = create_candidate_and_company
    candidate_token = create_token({"sub": candidate.email})
    company_token = create_token({"sub": company.email})
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
        (candidate_token, HTTPStatus.UNPROCESSABLE_ENTITY),
        (company_token, HTTPStatus.OK),
    ]:
        resp = client_app.post(
            url=jobs_create_url,
            content=payload.model_dump_json(),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == status
