import datetime

from decimal import Decimal

import pytest

from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from sqlalchemy.ext.asyncio import AsyncSession

from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.repository import EntryRepository
from modules.entry.schemas import EntryFilterSchema, EntrySummaryFilterSchema
from modules.entry.tests.fixtures.factories import EntryFactory
from modules.user.models import UserModel
from modules.user.tests.fixtures.factories import UserFactory


@pytest.mark.asyncio(loop_scope="session")
class TestEntryRepository:
    async def test_create_persists_entry_and_assigns_id(self, db_session: AsyncSession, user: UserModel):
        payment_date = datetime.date.today()
        repo = EntryRepository(db_session)
        entry = EntryModel(
            user_id=user.id,
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.CREDIT_CARD,
            amount=Decimal("10.50"),
            payment_date=payment_date,
            category="snack",
            description="Lunch",
            is_fixed=False,
        )

        result = await repo.create(entry)

        assert result.id is not None
        assert result.user_id == user.id
        assert result.entry_type == EntryTypeEnum.DEBIT
        assert result.amount == Decimal("10.50")
        assert result.category == "snack"
        assert result.description == "Lunch"
        assert result.is_fixed is False
        assert result.payment_date == payment_date

    async def test_get_by_user_id_returns_only_entries_for_user(
        self, db_session: AsyncSession, user: UserModel, entry: EntryModel
    ):
        UserFactory.__async_session__ = db_session
        EntryFactory.__async_session__ = db_session
        other_user = await UserFactory.create_async()
        second_entry = await EntryFactory.create_async(user=user, amount=Decimal("100.00"))
        await EntryFactory.create_async(user=other_user, amount=Decimal("9.99"))

        result = await EntryRepository(db_session).get_by_user_id(user.id)

        assert [result_entry.id for result_entry in result] == [entry.id, second_entry.id]
        assert all(result_entry.user_id == user.id for result_entry in result)

    async def test_get_by_user_id_returns_empty_list_when_user_has_no_entries(
        self, db_session: AsyncSession, user: UserModel
    ):
        result = await EntryRepository(db_session).get_by_user_id(user.id)

        assert result == []

    async def test_get_all_returns_only_entries_matching_filters(
        self,
        db_session: AsyncSession,
        user: UserModel,
    ):
        EntryFactory.__async_session__ = db_session
        UserFactory.__async_session__ = db_session
        today = datetime.date.today()
        matching_entry = await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=10),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=2),
            category="transport",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.CREDIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.CASH,
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=today - datetime.timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
            deleted_at=datetime.datetime.now(datetime.UTC),
        )
        other_user = await UserFactory.create_async()
        await EntryFactory.create_async(
            user=other_user,
            payment_date=today - datetime.timedelta(days=2),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        filters = EntryFilterSchema(
            start_date=today - datetime.timedelta(days=3),
            end_date=today - datetime.timedelta(days=1),
            category="snack",
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        set_params(Params(page=1, size=50))

        result = await EntryRepository(db_session).get_all(user.id, filters)

        assert result.total == 1
        assert [entry.id for entry in result.items] == [matching_entry.id]

    async def test_get_summary_returns_analytics_for_unfiltered_dimensions(
        self,
        db_session: AsyncSession,
        user: UserModel,
    ):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user=user,
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        await EntryFactory.create_async(
            user=user,
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.CASH,
        )
        await EntryFactory.create_async(
            user=user,
            entry_type=EntryTypeEnum.CREDIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        result = await EntryRepository(db_session).get_summary(user.id, EntrySummaryFilterSchema())

        assert result.by_entry_type == {
            EntryTypeEnum.DEBIT: 2,
            EntryTypeEnum.CREDIT: 1,
        }
        assert result.by_payment_method == {
            PaymentMethodEnum.DEBIT_CARD: 0,
            PaymentMethodEnum.CREDIT_CARD: 0,
            PaymentMethodEnum.PIX: 2,
            PaymentMethodEnum.CASH: 1,
            PaymentMethodEnum.ACCOUNT_TRANSFER: 0,
        }

    async def test_get_summary_returns_period_and_cumulative_balances(
        self,
        db_session: AsyncSession,
        user: UserModel,
    ):
        EntryFactory.__async_session__ = db_session
        start_date = datetime.date.today() - datetime.timedelta(days=10)
        end_date = datetime.date.today() - datetime.timedelta(days=1)
        await EntryFactory.create_async(
            user=user,
            payment_date=start_date - datetime.timedelta(days=1),
            amount=Decimal("100.00"),
            entry_type=EntryTypeEnum.DEBIT,
            category="other",
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=start_date,
            amount=Decimal("250.00"),
            entry_type=EntryTypeEnum.CREDIT,
            category="other",
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=end_date,
            amount=Decimal("50.00"),
            entry_type=EntryTypeEnum.DEBIT,
            category="other",
        )
        await EntryFactory.create_async(
            user=user,
            payment_date=end_date + datetime.timedelta(days=1),
            amount=Decimal("500.00"),
            entry_type=EntryTypeEnum.CREDIT,
            category="other",
        )
        result = await EntryRepository(db_session).get_summary(
            user.id,
            EntrySummaryFilterSchema(start_date=start_date, end_date=end_date),
        )

        assert result.last_balance == Decimal("-100.00")
        assert result.current_balance == Decimal("200.00")
        assert result.balance == Decimal("100.00")

    async def test_get_summary_counts_fixed_entries_monthly_from_payment_date(
        self,
        db_session: AsyncSession,
        user: UserModel,
    ):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user=user,
            payment_date=datetime.date(2026, 1, 31),
            amount=Decimal("1000.00"),
            entry_type=EntryTypeEnum.CREDIT,
            payment_method=PaymentMethodEnum.ACCOUNT_TRANSFER,
            is_fixed=True,
        )

        result = await EntryRepository(db_session).get_summary(
            user.id,
            EntrySummaryFilterSchema(
                start_date=datetime.date(2026, 2, 1),
                end_date=datetime.date(2026, 3, 31),
            ),
        )

        assert result.last_balance == Decimal("1000.00")
        assert result.current_balance == Decimal("2000.00")
        assert result.balance == Decimal("3000.00")
        assert result.by_entry_type == {
            EntryTypeEnum.DEBIT: 0,
            EntryTypeEnum.CREDIT: 2,
        }
        assert result.by_payment_method[PaymentMethodEnum.ACCOUNT_TRANSFER] == 2

    async def test_get_summary_excludes_fixed_entry_before_its_payment_date(
        self,
        db_session: AsyncSession,
        user: UserModel,
    ):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user=user,
            payment_date=datetime.date(2026, 3, 15),
            amount=Decimal("1000.00"),
            entry_type=EntryTypeEnum.CREDIT,
            is_fixed=True,
        )

        result = await EntryRepository(db_session).get_summary(
            user.id,
            EntrySummaryFilterSchema(
                start_date=datetime.date(2026, 2, 1),
                end_date=datetime.date(2026, 2, 28),
            ),
        )

        assert result.last_balance == Decimal("0.00")
        assert result.current_balance == Decimal("0.00")
        assert result.balance == Decimal("0.00")
        assert result.by_entry_type == {
            EntryTypeEnum.DEBIT: 0,
            EntryTypeEnum.CREDIT: 0,
        }
