from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.finance.enums import EntryTypeEnum, PaymentMethodEnum
from modules.finance.models import EntryModel
from modules.finance.schemas import EntryFilterSchema, EntryPage, EntrySummaryFilterSchema, EntrySummarySchema


class EntryRepository(BaseRepository[EntryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EntryModel)

    async def add_batch(self, entries: list[EntryModel]) -> list[EntryModel]:
        self._session.add_all(entries)
        await self._session.flush()
        return entries

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

    async def get_summary(self, user_id: UUID, query_params: EntrySummaryFilterSchema) -> EntrySummarySchema:
        end_date = query_params.end_date or date.today()

        signed_amount = case(
            (EntryModel.entry_type == EntryTypeEnum.CREDIT, EntryModel.amount),
            else_=-EntryModel.amount,
        )
        base_filters = (
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )

        balance_statement = select(func.coalesce(func.sum(signed_amount), 0)).where(
            *base_filters,
            EntryModel.payment_date <= end_date,
        )
        balance = await self._session.scalar(balance_statement)

        last_balance = None
        if query_params.start_date:
            last_balance_statement = select(func.coalesce(func.sum(signed_amount), 0)).where(
                *base_filters,
                EntryModel.payment_date < query_params.start_date,
            )
            last_balance = await self._session.scalar(last_balance_statement)

        current_balance_statement = select(func.coalesce(func.sum(signed_amount), 0)).where(
            *base_filters,
            EntryModel.payment_date <= end_date,
        )
        if query_params.start_date:
            current_balance_statement = current_balance_statement.where(
                EntryModel.payment_date >= query_params.start_date
            )
        current_balance = await self._session.scalar(current_balance_statement)

        analytics_statement = select(
            *(
                func.count().filter(EntryModel.entry_type == entry_type).label(f"entry_type_{entry_type.value}")
                for entry_type in EntryTypeEnum
            ),
            *(
                func.count()
                .filter(EntryModel.payment_method == payment_method)
                .label(f"payment_method_{payment_method.value}")
                for payment_method in PaymentMethodEnum
            ),
        ).where(
            *base_filters,
            EntryModel.payment_date <= end_date,
        )
        if query_params.start_date:
            analytics_statement = analytics_statement.where(EntryModel.payment_date >= query_params.start_date)
        analytics = (await self._session.execute(analytics_statement)).one()

        return EntrySummarySchema(
            last_balance=last_balance,
            current_balance=current_balance or Decimal("0.00"),
            balance=balance or Decimal("0.00"),
            by_entry_type={
                entry_type: getattr(analytics, f"entry_type_{entry_type.value}") for entry_type in EntryTypeEnum
            },
            by_payment_method={
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
