from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.entry.models import EntryModel


class EntryRepository(BaseRepository[EntryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EntryModel)

    async def get_by_user_id(self, user_id: UUID) -> list[EntryModel]:
        return list(await self._session.scalars(select(EntryModel).where(EntryModel.user_id == user_id)))
