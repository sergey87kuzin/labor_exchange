import logging
from dataclasses import asdict

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from dependencies import get_current_user
from dependencies.containers import RepositoriesContainer
from models import User
from repositories import UserRepository
from tools.security import hash_password
from web.schemas import PaginationSchema, UserCreateSchema, UserSchema, UserUpdateSchema
from web.schemas.user_with_jobs_and_responses import UserSchemaWithJobAndResponse

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger()


@router.get("")
@inject
async def read_users(
    pagination: PaginationSchema = Depends(),
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> list[UserSchema]:
    if current_user and current_user.is_company:
        show_companies = False
    else:
        show_companies = True
    users_model = await user_repository.retrieve_many(
        pagination.limit, pagination.skip, show_companies
    )
    users_schema = [UserSchema(**asdict(user)) for user in users_model]
    return users_schema


@router.get("/me")
@inject
async def me(
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchemaWithJobAndResponse:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован",
        )
    try:
        user_model = await user_repository.retrieve(include_relations=True, id=current_user.id)
        return UserSchemaWithJobAndResponse(**asdict(user_model))
    except ValueError:
        logger.warning(f"Ошибка получения данных о своем аккаунте: {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )


@router.get("/{user_id}")
@inject
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema:
    """Соискатель может посмотреть компанию и наоборот"""
    if current_user and current_user.is_company:
        is_company = False
    else:
        is_company = True
    try:
        user_model = await user_repository.retrieve(
            include_relations=True, id=user_id, is_company=is_company
        )
        return UserSchema(**asdict(user_model))
    except ValueError:
        logger.warning(
            f"Ошибка при получении данных о чужом аккаунте: {current_user.id} запрашивал {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )


@router.post("")
@inject
async def create_user(
    user_create_dto: UserCreateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
) -> UserSchema:
    try:
        existing_user = await user_repository.retrieve(email=user_create_dto.email)
    except ValueError:
        # Пользователя с такой почтой не существует
        pass
    else:
        logger.warning(
            f"Попытка повторной регистрации пользователя с почтой: {user_create_dto.email}"
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже существует",
            )
    try:
        user = await user_repository.create(
            user_create_dto, hashed_password=hash_password(user_create_dto.password)
        )
        return UserSchema(**asdict(user))
    except IntegrityError:
        logger.warning(f"Ошибка при создании пользователя. email: {user_create_dto.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректные данные пользователя",
        )


@router.patch("")
@inject
async def update_user(
    user_update_schema: UserUpdateSchema,
    user_repository: UserRepository = Depends(Provide[RepositoriesContainer.user_repository]),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    try:
        existing_user = await user_repository.retrieve(email=user_update_schema.email)
    except ValueError:
        logger.warning(f"Не найден пользователь для изменения: {user_update_schema.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь с такой почтой не найден"
        )

    if existing_user and existing_user.id != current_user.id:
        logger.warning(
            f"Попытка изменения другого пользователя: {current_user.id}"
            f" пытался менять {existing_user.id}"
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недостаточно прав")

    try:
        updated_user = await user_repository.update(current_user.id, user_update_schema)
        return UserSchema(**asdict(updated_user))

    except ValueError:
        logger.warning(f"Не найден пользователь для изменения: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
