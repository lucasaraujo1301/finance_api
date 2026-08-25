from typing import Annotated

from fastapi import Depends

from modules.core.database import AsyncDbDep
from modules.core.logger import logger
from modules.entry.repository import EntryRepository
from modules.entry.services import EntryService
from modules.user.dependencies import UserServiceDep


def get_entry_repository(db_session: AsyncDbDep) -> EntryRepository:
    return EntryRepository(db_session)


def get_entry_service(
    entry_repository: EntryRepositoryDep,
    user_service: UserServiceDep,
) -> EntryService:
    return EntryService(logger, entry_repository, user_service)


EntryServiceDep = Annotated[EntryService, Depends(get_entry_service)]
EntryRepositoryDep = Annotated[EntryRepository, Depends(get_entry_repository)]
