from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from interfaces import IRepositoryAsync
from models import User as UserModel
from storage.sqlalchemy.tables import User
from tools.to_model import ToModel
from web.schemas import UserCreateSchema, UserUpdateSchema


class UserRepository(IRepositoryAsync):
    def __init__(self, session: Callable[..., AbstractContextManager[Session]]):
        self.session = session

    async def create(self, user_create_dto: UserCreateSchema, hashed_password: str) -> UserModel:
        async with self.session() as session:
            user = User(
                name=user_create_dto.name,
                email=user_create_dto.email,
                is_company=user_create_dto.is_company,
                hashed_password=hashed_password,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

        return ToModel().to_user_model(user_from_db=user, include_relations=False)

    async def retrieve(self, include_relations: bool = False, **kwargs) -> UserModel | None:
        async with self.session() as session:
            query = select(User).filter_by(**kwargs).limit(1)
            if include_relations:
                query = query.options(selectinload(User.jobs)).options(selectinload(User.responses))

            res = await session.execute(query)
            user_from_db = res.scalars().first()
        if not user_from_db:
            return None
        return ToModel().to_user_model(
            user_from_db=user_from_db, include_relations=include_relations
        )

    async def retrieve_many(
        self,
        limit: int = 100,
        skip: int = 0,
        include_relations: bool = False,
        show_companies: bool = False,
    ) -> list[UserModel]:
        async with self.session() as session:
            query = select(User).filter_by(is_company=show_companies).limit(limit).offset(skip)
            if include_relations:
                query = query.options(selectinload(User.jobs)).options(selectinload(User.responses))

            res = await session.execute(query)
            users_from_db = res.scalars().all()

        users_model = []
        for user in users_from_db:
            model = ToModel().to_user_model(user_from_db=user, include_relations=include_relations)
            users_model.append(model)

        return users_model

    async def update(self, id: int, user_update_dto: UserUpdateSchema) -> UserModel | None:
        async with self.session() as session:
            query = select(User).filter_by(id=id).limit(1)
            res = await session.execute(query)
            user_from_db = res.scalars().first()

            if not user_from_db:
                return None

            name = user_update_dto.name if user_update_dto.name is not None else user_from_db.name
            email = (
                user_update_dto.email if user_update_dto.email is not None else user_from_db.email
            )
            is_company = (
                user_update_dto.is_company
                if user_update_dto.is_company is not None
                else user_from_db.is_company
            )

            user_from_db.name = name
            user_from_db.email = email
            user_from_db.is_company = is_company

            session.add(user_from_db)
            await session.commit()
            await session.refresh(user_from_db)

        new_user = ToModel().to_user_model(user_from_db=user_from_db, include_relations=False)
        return new_user

    async def delete(self, user_id: int) -> UserModel | None:
        async with self.session() as session:
            query = select(User).filter_by(id=user_id).limit(1)
            res = await session.execute(query)
            user_from_db = res.scalars().first()

            if user_from_db:
                await session.delete(user_from_db)
                await session.commit()
            else:
                return None

        return ToModel().to_user_model(user_from_db=user_from_db, include_relations=False)

    # @staticmethod
    # def __to_user_model(user_from_db: User, include_relations: bool = False) -> UserModel:
    #     user_jobs = []
    #     user_responses = []
    #     user_model = None
    #
    #     if user_from_db:
    #         if include_relations:
    #             if user_from_db.is_company:
    #                 user_jobs = [
    #                     JobModel(
    #                         id=job.id,
    #                         salary_to=job.salary_to,
    #                         salary_from=job.salary_from,
    #                         title=job.title,
    #                         description=job.description,
    #                         is_active=job.is_active,
    #                     )
    #                     for job in user_from_db.jobs
    #                 ]
    #             else:
    #                 user_responses = [
    #                     ResponseModel(id=response.id, message=response.message)
    #                     for response in user_from_db.responses
    #                 ]
    #
    #         user_model = UserModel(
    #             id=user_from_db.id,
    #             name=user_from_db.name,
    #             email=user_from_db.email,
    #             hashed_password=user_from_db.hashed_password,
    #             is_company=user_from_db.is_company,
    #             jobs=user_jobs,
    #             responses=user_responses,
    #         )
    #
    #     return user_model
