from uuid import UUID

from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryFilterSchema


class EntryRepository(BaseRepository[EntryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EntryModel)

    async def get_by_user_id(self, user_id: UUID) -> list[EntryModel]:
        return list(await self._session.scalars(select(EntryModel).where(EntryModel.user_id == user_id)))

    async def get_all(self, user_id: UUID, query_params: EntryFilterSchema) -> Page[EntryModel]:
        statement = select(EntryModel).where(
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )

        if query_params.start_date:
            statement = statement.where(EntryModel.payment_date >= query_params.start_date)

        if query_params.end_date:
            statement = statement.where(EntryModel.payment_date <= query_params.end_date)

        if query_params.category:
            statement = statement.where(EntryModel.category == query_params.category)

        if query_params.entry_type:
            statement = statement.where(EntryModel.entry_type == query_params.entry_type)

        if query_params.payment_method:
            statement = statement.where(EntryModel.payment_method == query_params.payment_method)

        statement = statement.order_by(
            EntryModel.payment_date.desc(),
            EntryModel.created_at.desc(),
            EntryModel.id.desc(),
        )

        return await paginate(self._session, statement)
