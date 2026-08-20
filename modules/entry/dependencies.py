from typing import Annotated

from fastapi import Depends

from modules.core.database import AsyncDbDep
from modules.core.logger import logger
from modules.entry.services import EntryService
from modules.user.dependencies import UserServiceDep


def get_entry_service(
    db_session: AsyncDbDep,
    user_service: UserServiceDep,
) -> EntryService:
    return EntryService(logger, db_session, user_service)


EntryServiceDep = Annotated[EntryService, Depends(get_entry_service)]
