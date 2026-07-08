from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.user.services import UserService


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)
