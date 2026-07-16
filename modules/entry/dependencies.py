from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.logger import logger
from modules.entry.services import EntryService


def get_entry_service(db_session: AsyncSession = Depends(get_db)):
    return EntryService(logger, db_session)
