from typing import Annotated

import jwt

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from modules.core.database import AsyncDbDep
from modules.core.logger import logger
from modules.user.config import user_settings
from modules.user.exceptions import InvalidCredentials, SuperuserRequired, UserNotFound
from modules.user.models import UserModel
from modules.user.services import AuthService, UserService

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_service(db: AsyncDbDep) -> UserService:
    return UserService(logger, db, password_hash)


async def get_auth_service(
    user_service: UserServiceDep,
) -> AuthService:
    return AuthService(user_service, password_hash, user_settings)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    user_service: UserServiceDep,
) -> UserModel:
    if credentials is None:
        raise InvalidCredentials()

    try:
        payload = jwt.decode(
            credentials.credentials,
            user_settings.JWT_SECRET_KEY,
            algorithms=[user_settings.JWT_ALGORITHM],
            audience=user_settings.JWT_AUDIENCE,
            issuer=user_settings.JWT_ISSUER,
        )
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Access token required")

        return await user_service.get_by_id(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, UserNotFound) as error:
        raise InvalidCredentials() from error


async def require_superuser(
    user: CurrentUser,
) -> UserModel:
    if not user.is_superuser:
        raise SuperuserRequired()

    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
Superuser = Annotated[UserModel, Depends(require_superuser)]
