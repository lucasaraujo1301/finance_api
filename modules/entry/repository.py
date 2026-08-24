from datetime import date
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryFilterSchema, EntryPage, EntrySummarySchema


class EntryRepository(BaseRepository[EntryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EntryModel)

    async def get_by_user_id(self, user_id: UUID) -> list[EntryModel]:
        return list(await self._session.scalars(select(EntryModel).where(EntryModel.user_id == user_id)))

    async def get_all(self, user_id: UUID, query_params: EntryFilterSchema) -> EntryPage:
        statement = select(EntryModel).where(
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )
        statement = self._apply_filters(statement, query_params)

        statement = statement.order_by(
            EntryModel.payment_date.desc(),
            EntryModel.created_at.desc(),
            EntryModel.id.desc(),
        )

        return await apaginate(self._session, statement)

    async def get_summary(self, user_id: UUID, query_params: EntryFilterSchema) -> EntrySummarySchema:
        end_date = query_params.end_date or date.today()
        signed_amount = case(
            (EntryModel.entry_type == EntryTypeEnum.CREDIT, EntryModel.amount),
            else_=-EntryModel.amount,
        )
        balance_filters = (
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )
        balance = await self._session.scalar(
            select(func.coalesce(func.sum(signed_amount), 0)).where(
                *balance_filters,
                EntryModel.payment_date <= end_date,
            )
        )

        last_balance = None
        if query_params.start_date:
            last_balance = await self._session.scalar(
                select(func.coalesce(func.sum(signed_amount), 0)).where(
                    *balance_filters,
                    EntryModel.payment_date < query_params.start_date,
                )
            )

        current_balance_filters = [*balance_filters, EntryModel.payment_date <= end_date]
        if query_params.start_date:
            current_balance_filters.append(EntryModel.payment_date >= query_params.start_date)
        current_balance = await self._session.scalar(
            select(func.coalesce(func.sum(signed_amount), 0)).where(*current_balance_filters)
        )

        analytics_statement = select(
            *(func.count().filter(EntryModel.entry_type == entry_type).label(f"entry_type_{entry_type.value}")
              for entry_type in EntryTypeEnum),
            *(func.count().filter(EntryModel.payment_method == payment_method).label(
                f"payment_method_{payment_method.value}"
            ) for payment_method in PaymentMethodEnum),
        ).where(*balance_filters)
        analytics = (await self._session.execute(self._apply_filters(analytics_statement, query_params))).one()

        return EntrySummarySchema(
            last_balance=last_balance,
            current_balance=current_balance,
            balance=balance,
            by_entry_type=None if query_params.entry_type else {
                entry_type: getattr(analytics, f"entry_type_{entry_type.value}") for entry_type in EntryTypeEnum
            },
            by_payment_method=None if query_params.payment_method else {
                payment_method: getattr(analytics, f"payment_method_{payment_method.value}")
                for payment_method in PaymentMethodEnum
            },
        )

    @staticmethod
    def _apply_filters(statement, query_params: EntryFilterSchema):
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
        return statement
