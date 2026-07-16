from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.entry.models import Entry


class EntryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entry: Entry) -> Entry:
        self._session.add(entry)
        await self._session.commit()
        await self._session.refresh(entry)
        return entry

    async def get_by_user_id(self, user_id: UUID) -> list[Entry]:
        return list(await self._session.scalars(select(Entry).where(Entry.user_id == user_id)))
