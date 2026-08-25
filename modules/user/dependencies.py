from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash

from modules.core.database import AsyncDbDep
from modules.core.logger import logger
from modules.user.config import user_settings
from modules.user.exceptions import InvalidCredentials, InvalidPasswordUpdateToken, SuperuserRequired
from modules.user.models import UserModel
from modules.user.repository import UserRepository
from modules.user.services import AuthService, UserService

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


async def get_user_repository(db: AsyncDbDep) -> UserRepository:
    return UserRepository(db)

async def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(logger, repository, password_hash)


async def get_auth_service(
    user_service: UserServiceDep,
) -> AuthService:
    return AuthService(user_service, password_hash, user_settings)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
) -> UserModel:
    if credentials is None:
        raise InvalidCredentials()

    return await auth_service.get_user_from_jwt(credentials.credentials, "access", InvalidCredentials)


async def require_superuser(
    user: CurrentUser,
) -> UserModel:
    if not user.is_superuser:
        raise SuperuserRequired()

    return user


async def get_current_user_from_password_setup(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
) -> UserModel:
    if credentials is None:
        raise InvalidPasswordUpdateToken()

    user = await auth_service.get_user_from_jwt(
        credentials.credentials,
        "password_setup",
        InvalidPasswordUpdateToken,
    )
    if not user.needs_password_update:
        raise InvalidPasswordUpdateToken()

    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
Superuser = Annotated[UserModel, Depends(require_superuser)]
PasswordSetupUser = Annotated[UserModel, Depends(get_current_user_from_password_setup)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
