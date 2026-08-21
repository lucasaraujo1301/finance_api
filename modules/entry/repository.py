from datetime import date
from uuid import UUID

from fastapi_pagination.config import Config
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy import Numeric, case, cast, func, null, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryFilterSchema, EntryPage


class EntryRepository(BaseRepository[EntryModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, EntryModel)

    async def get_by_user_id(self, user_id: UUID) -> list[EntryModel]:
        return list(await self._session.scalars(select(EntryModel).where(EntryModel.user_id == user_id)))

    async def get_all(self, user_id: UUID, query_params: EntryFilterSchema) -> EntryPage:
        end_date = query_params.end_date or date.today()
        signed_amount = case(
            (EntryModel.entry_type == EntryTypeEnum.CREDIT, EntryModel.amount),
            else_=-EntryModel.amount,
        )
        balance_filters = (
            EntryModel.user_id == user_id,
            EntryModel.deleted_at.is_(None),
        )
        balance = (
            select(func.coalesce(func.sum(signed_amount), 0))
            .where(*balance_filters, EntryModel.payment_date <= end_date)
            .scalar_subquery()
            .label("balance")
        )

        if query_params.start_date:
            last_balance = (
                select(func.coalesce(func.sum(signed_amount), 0))
                .where(*balance_filters, EntryModel.payment_date < query_params.start_date)
                .scalar_subquery()
                .label("last_balance")
            )
            current_balance = (
                select(func.coalesce(func.sum(signed_amount), 0))
                .where(
                    *balance_filters,
                    EntryModel.payment_date >= query_params.start_date,
                    EntryModel.payment_date <= end_date,
                )
                .scalar_subquery()
                .label("current_balance")
            )
        else:
            last_balance = cast(null(), Numeric(12, 2)).label("last_balance")
            current_balance = (
                select(func.coalesce(func.sum(signed_amount), 0))
                .where(*balance_filters, EntryModel.payment_date <= end_date)
                .scalar_subquery()
                .label("current_balance")
            )

        analytics = []
        if query_params.entry_type is None:
            analytics.extend(
                func.count().filter(EntryModel.entry_type == entry_type).over().label(f"entry_type_{entry_type.value}")
                for entry_type in EntryTypeEnum
            )

        if query_params.payment_method is None:
            analytics.extend(
                func.count()
                .filter(EntryModel.payment_method == payment_method)
                .over()
                .label(f"payment_method_{payment_method.value}")
                for payment_method in PaymentMethodEnum
            )

        statement = select(EntryModel, last_balance, current_balance, balance, *analytics).where(
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

        additional_data = {
            "last_balance": None,
            "current_balance": 0,
            "balance": 0,
            "by_entry_type": None,
            "by_payment_method": None,
        }

        def transform(rows):
            if rows:
                first_row = rows[0]
                additional_data["last_balance"] = first_row.last_balance
                additional_data["current_balance"] = first_row.current_balance
                additional_data["balance"] = first_row.balance
                if query_params.entry_type is None:
                    additional_data["by_entry_type"] = {
                        entry_type: getattr(first_row, f"entry_type_{entry_type.value}") for entry_type in EntryTypeEnum
                    }
                if query_params.payment_method is None:
                    additional_data["by_payment_method"] = {
                        payment_method: getattr(first_row, f"payment_method_{payment_method.value}")
                        for payment_method in PaymentMethodEnum
                    }

            return [row[0] for row in rows]

        return await apaginate(
            self._session,
            statement,
            unwrap_mode="no-unwrap",
            transformer=transform,
            additional_data=additional_data,
            config=Config(page_cls=EntryPage),
        )
