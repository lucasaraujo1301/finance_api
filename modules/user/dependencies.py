from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.logger import logger
from modules.user.services import UserService


async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(logger, db)
