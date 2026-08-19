from typing import Annotated

from fastapi import Depends
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.logger import logger
from modules.user.config import user_settings
from modules.user.services import AuthService, UserService

password_hash = PasswordHash.recommended()


async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(logger, db, password_hash)


async def get_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> AuthService:
    return AuthService(user_service, password_hash, user_settings)
