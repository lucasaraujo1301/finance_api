from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.user.exceptions import ApiKeyMissing
from modules.user.models import User
from modules.user.services import UserService

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


async def get_current_user(
    api_key: str | None = Depends(api_key_header), user_service: UserService = Depends(get_user_service)
) -> User:
    if not api_key:
        raise ApiKeyMissing()

    return await user_service.get_user_by_api_key(api_key)
