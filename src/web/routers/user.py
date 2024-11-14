from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from services.user_service import UserService
from tools.security import JWTBearer
from web.schemas import UserCreateSchema, UserSchema, UserUpdateSchema
from web.schemas.pagination import PaginationSchema
from web.schemas.user_with_jobs_and_responses import UserSchemaWithJobAndResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
@inject
async def read_users(
    pagination: PaginationSchema = Depends(),
    token: str = Depends(JWTBearer(auto_error=False)),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> list[UserSchema]:
    return await UserService(user_repository).get_all_users(
        pagination.limit, pagination.skip, token
    )


@router.get("/me")
@inject
async def me(
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchemaWithJobAndResponse | None:
    return await UserService(user_repository).get_me(current_user)


@router.get("/{user_id}")
@inject
async def read_user(
    user_id: int,
    token: str = Depends(JWTBearer(auto_error=False)),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema | None:
    return await UserService(user_repository).get_user(user_id, token)


@router.post("")
@inject
async def create_user(
    user_create_dto: UserCreateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema | None:
    return await UserService(user_repository).create_user(user_create_dto)


@router.patch("")
@inject
async def update_user(
    user_update_schema: UserUpdateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
) -> UserSchema | None:
    return await UserService(user_repository).update_user(user_update_schema, current_user)


@router.delete("")
@inject
async def delete_user(
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
):
    return await UserService(user_repository).delete_user(current_user)
