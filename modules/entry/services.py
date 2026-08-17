from logging import Logger
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.entry.models import EntryModel
from modules.entry.repository import EntryRepository
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema, TelegramEntryRequestSchema
from modules.user.services import UserService


class EntryService:
    def __init__(self, logger: Logger, db_session: AsyncSession):
        self.logger = logger
        self._entry_repository = EntryRepository(db_session)
        self._user_service = UserService(logger, db_session)

    async def create(
        self,
        user_id: UUID,
        data: EntryRequestSchema,
        created_by_service_account_id: UUID | None = None,
    ) -> EntryModel:
        self.logger.info("Creating new entry", extra={"user_id": str(user_id)})
        entry = EntryModel(
            user_id=user_id,
            created_by_service_account_id=created_by_service_account_id,
            **data.model_dump(),
        )

        return await self._entry_repository.create(entry)

    async def create_from_telegram(
        self,
        data: TelegramEntryRequestSchema,
        service_account_id: UUID,
    ) -> EntryModel:
        user = await self._user_service.get_by_telegram_id(data.telegram_id)
        entry_data = EntryRequestSchema.model_validate(data.model_dump(exclude={"telegram_id"}))

        return await self.create(
            user_id=user.id,
            data=entry_data,
            created_by_service_account_id=service_account_id,
        )

    async def get_all(self, user_id: UUID, query_params: EntryFilterSchema):
        return await self._entry_repository.get_all(user_id, query_params)
