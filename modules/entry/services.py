from logging import Logger
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.entry.models import EntryModel
from modules.entry.repository import EntryRepository
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema


class EntryService:
    def __init__(self, logger: Logger, db_session: AsyncSession):
        self.logger = logger
        self._entry_repository = EntryRepository(db_session)

    async def create(self, user_id: UUID, data: EntryRequestSchema) -> EntryModel:
        self.logger.info("Creating new entry", extra={"user_id": str(user_id)})
        entry = EntryModel(user_id=user_id, **data.model_dump())

        return await self._entry_repository.create(entry)

    async def get_all(self, user_id: UUID, query_params: EntryFilterSchema):
        return await self._entry_repository.get_all(user_id, query_params)
