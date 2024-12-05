from fastapi import HTTPException, status

from repositories import UserRepository
from tools.security import decode_token


async def get_user_from_token(token: str, user_repository: UserRepository):
    cred_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Учетные данные недействительны"
    )
    payload = decode_token(token)
    if payload is None:
        raise cred_exception
    email: str = payload.get("sub")
    if email is None:
        raise cred_exception
    user = await user_repository.retrieve(email=email, include_relations=False)
    if user is None:
        raise cred_exception
    return user
