from models import Response as ResponseModel
from models import User as UserModel
from models.job import Job as JobModel
from storage.sqlalchemy.tables import Job, Response, User


class ToModel:
    @staticmethod
    def to_user_model(user_from_db: User, include_relations: bool = False) -> UserModel:
        user_jobs = []
        user_responses = []
        user_model = None

        if user_from_db:
            if include_relations:
                if user_from_db.is_company:
                    user_jobs = [
                        JobModel(
                            id=job.id,
                            salary_to=job.salary_to,
                            salary_from=job.salary_from,
                            title=job.title,
                            description=job.description,
                            is_active=job.is_active,
                        )
                        for job in user_from_db.jobs
                    ]
                else:
                    user_responses = [
                        ResponseModel(id=response.id, message=response.message)
                        for response in user_from_db.responses
                    ]

            user_model = UserModel(
                id=user_from_db.id,
                name=user_from_db.name,
                email=user_from_db.email,
                hashed_password=user_from_db.hashed_password,
                is_company=user_from_db.is_company,
                jobs=user_jobs,
                responses=user_responses,
            )

        return user_model

    @staticmethod
    def to_job_model(job_from_db: Job, include_relations: bool = False) -> JobModel | None:
        if not job_from_db:
            return None

        job_model = JobModel(
            id=job_from_db.id,
            title=job_from_db.title,
            description=job_from_db.description,
            salary_from=job_from_db.salary_from,
            salary_to=job_from_db.salary_to,
            is_active=job_from_db.is_active,
            created_at=job_from_db.created_at,
            user=None,
        )
        if include_relations:
            user = UserModel(
                id=job_from_db.user.id,
                name=job_from_db.user.name,
                email=job_from_db.user.email,
                is_company=job_from_db.user.is_company,
            )
            job_model.user = user

        return job_model

    @staticmethod
    def to_response_model(
        response_from_db: Response, with_user: bool = False, with_job: bool = False
    ) -> ResponseModel | None:
        if not response_from_db:
            return None

        response_model = ResponseModel(
            id=response_from_db.id,
            message=response_from_db.message,
            user_id=response_from_db.user_id,
            user=None,
            job=None,
        )
        if with_user:
            user = UserModel(
                id=response_from_db.id,
                name=response_from_db.user.name,
                email=response_from_db.user.email,
                is_company=response_from_db.user.is_company,
            )
            response_model.user = user
        if with_job:
            job = JobModel(
                id=response_from_db.job.id,
                title=response_from_db.job.title,
                description=response_from_db.job.description,
                salary_from=response_from_db.job.salary_from,
                salary_to=response_from_db.job.salary_to,
                is_active=response_from_db.job.is_active,
                user_id=response_from_db.job.user_id,
            )
            response_model.job = job

        return response_model
