from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.logger import logger
from modules.entry.services import EntryService
from modules.user.dependencies import get_user_service
from modules.user.services import UserService


def get_entry_service(
    db_session: Annotated[AsyncSession, Depends(get_db)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> EntryService:
    return EntryService(logger, db_session, user_service)
