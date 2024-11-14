from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from tools.get_user_from_token import get_user_from_token
from tools.security import JWTBearer


@inject
async def get_current_user(
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    token: str = Depends(JWTBearer()),
) -> User:
    return await get_user_from_token(token, user_repository)
