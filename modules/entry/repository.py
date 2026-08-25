from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import Date, Interval, case, cast, func, literal, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryFilterSchema, EntryPage, EntrySummaryFilterSchema, EntrySummarySchema


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

    async def get_summary(self, user_id: UUID, query_params: EntrySummaryFilterSchema) -> EntrySummarySchema:
        end_date = query_params.end_date or date.today()
        entries_statement = select(EntryModel).where(
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )
        entries = entries_statement.cte("summary_entries")

        one_month = cast(literal("1 month"), Interval)
        one_day = cast(literal("1 day"), Interval)
        months = (
            func.generate_series(
                func.date_trunc("month", entries.c.payment_date),
                func.date_trunc("month", end_date),
                one_month,
            )
            .table_valued("month_start")
            .render_derived()
            .lateral()
        )
        last_day = func.date_trunc("month", months.c.month_start) + one_month - one_day
        occurrence_date = cast(
            months.c.month_start
            + (func.least(func.extract("day", entries.c.payment_date), func.extract("day", last_day)) - 1) * one_day,
            Date,
        )
        recurring_entries = (
            select(
                entries.c.amount,
                entries.c.entry_type,
                entries.c.payment_method,
                entries.c.category,
                occurrence_date.label("occurrence_date"),
            )
            .select_from(entries.join(months, true()))
            .where(entries.c.is_fixed.is_(True), occurrence_date >= entries.c.payment_date)
        )
        one_time_entries = select(
            entries.c.amount,
            entries.c.entry_type,
            entries.c.payment_method,
            entries.c.category,
            entries.c.payment_date.label("occurrence_date"),
        ).where(entries.c.is_fixed.is_(False))
        occurrences = recurring_entries.union_all(one_time_entries).cte("entry_occurrences")

        signed_amount = case(
            (occurrences.c.entry_type == EntryTypeEnum.CREDIT, occurrences.c.amount),
            else_=-occurrences.c.amount,
        )
        balance = await self._session.scalar(
            select(func.coalesce(func.sum(signed_amount), 0)).where(
                occurrences.c.occurrence_date <= end_date,
            )
        )

        last_balance = None
        if query_params.start_date:
            last_balance = await self._session.scalar(
                select(func.coalesce(func.sum(signed_amount), 0)).where(
                    occurrences.c.occurrence_date < query_params.start_date,
                )
            )

        current_balance_statement = select(func.coalesce(func.sum(signed_amount), 0)).where(
            occurrences.c.occurrence_date <= end_date
        )
        if query_params.start_date:
            current_balance_statement = current_balance_statement.where(
                occurrences.c.occurrence_date >= query_params.start_date
            )
        current_balance = await self._session.scalar(current_balance_statement)

        analytics_statement = select(
            *(
                func.count().filter(occurrences.c.entry_type == entry_type).label(f"entry_type_{entry_type.value}")
                for entry_type in EntryTypeEnum
            ),
            *(
                func.count()
                .filter(occurrences.c.payment_method == payment_method)
                .label(f"payment_method_{payment_method.value}")
                for payment_method in PaymentMethodEnum
            ),
        ).where(occurrences.c.occurrence_date <= end_date)
        if query_params.start_date:
            analytics_statement = analytics_statement.where(occurrences.c.occurrence_date >= query_params.start_date)
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
