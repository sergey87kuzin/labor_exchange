from dataclasses import asdict

from fastapi import HTTPException, status

from repositories import UserRepository
from storage.sqlalchemy.tables import User
from tools.get_user_from_token import get_user_from_token
from tools.security import hash_password
from web.schemas import UserCreateSchema, UserSchema, UserUpdateSchema
from web.schemas.user_with_jobs_and_responses import UserSchemaWithJobAndResponse


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_create_dto: UserCreateSchema) -> UserSchema | None:
        existing_user = await self.user_repository.retrieve(email=user_create_dto.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже существует",
            )
        user = await self.user_repository.create(
            user_create_dto, hashed_password=hash_password(user_create_dto.password)
        )
        return UserSchema(**asdict(user))

    async def get_user(self, user_id: int, token: str = None) -> UserSchema | None:
        """Соискатель может посмотреть компанию и наоборот"""
        current_user = None
        if token:
            current_user = await get_user_from_token(token, self.user_repository)
        if current_user and current_user.is_company:
            is_company = False
        else:
            is_company = True
        user_model = await self.user_repository.retrieve(
            include_relations=True, id=user_id, is_company=is_company
        )
        if not user_model:
            return None
        return UserSchema(**asdict(user_model))

    async def get_me(self, current_user) -> UserSchemaWithJobAndResponse | None:
        user_model = await self.user_repository.retrieve(include_relations=True, id=current_user.id)
        if not user_model:
            return None
        return UserSchemaWithJobAndResponse(**asdict(user_model))

    async def update_user(
        self, user_update_schema: UserUpdateSchema, current_user: User
    ) -> UserSchema | None:
        existing_user = await self.user_repository.retrieve(email=user_update_schema.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав"
            )

        updated_user = await self.user_repository.update(current_user.id, user_update_schema)
        if not updated_user:
            return None
        return UserSchema(**asdict(updated_user))

    async def delete_user(self, current_user) -> UserSchema | None:
        user_from_db = await self.user_repository.delete(current_user.id)
        if not user_from_db:
            return None
        return UserSchema(**asdict(user_from_db))

    async def get_all_users(self, limit: int, skip: int, token: str = None) -> list[UserSchema]:
        current_user = None
        if token:
            current_user = await get_user_from_token(token, self.user_repository)
        if current_user and current_user.is_company:
            show_companies = False
        else:
            show_companies = True
        users_model = await self.user_repository.retrieve_many(limit, skip, show_companies)

        users_schema = [UserSchema(**asdict(user)) for user in users_model]
        return users_schema
