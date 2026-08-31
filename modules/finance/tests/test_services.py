from datetime import date
from decimal import Decimal

import pytest

from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from sqlalchemy.ext.asyncio import AsyncSession

from modules.finance.enums import EntryTypeEnum, PaymentMethodEnum
from modules.finance.models import EntryModel
from modules.finance.schemas import (
    EntryFilterSchema,
    EntryRequestSchema,
    EntrySummaryFilterSchema,
    TelegramEntryRequestSchema,
)
from modules.finance.tests.fixtures.factories import EntryFactory
from modules.service_account.models import ServiceAccountModel
from modules.user.exceptions import UserNotFound
from modules.user.models import UserModel


@pytest.mark.asyncio(loop_scope="session")
class TestEntryService:
    async def test_create_persists_and_returns_entry(
        self,
        db_session: AsyncSession,
        user: UserModel,
        entry_service,
    ):
        payment_date = date.today()
        data = EntryRequestSchema(
            amount=Decimal("10.50"),
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
            category="snack",
            description="Lunch",
            payment_date=payment_date,
        )
        result = await entry_service.create(user.id, data)

        persisted = await db_session.get(EntryModel, result.id)
        assert persisted is not None
        assert persisted.id == result.id
        assert result.user_id == user.id
        assert result.amount == Decimal("10.50")
        assert result.entry_type == EntryTypeEnum.DEBIT
        assert result.payment_method == PaymentMethodEnum.PIX
        assert result.category == "snack"
        assert result.description == "Lunch"
        assert result.payment_date == payment_date

    async def test_create_from_telegram_validates_user_and_delegates_creation(
        self,
        db_session: AsyncSession,
        user: UserModel,
        service_account: ServiceAccountModel,
        entry_service,
    ):
        data = TelegramEntryRequestSchema(
            telegram_id=user.telegram_id,
            amount=Decimal("10.50"),
            payment_method=PaymentMethodEnum.PIX,
            category="snack",
        )
        result = await entry_service.create_from_telegram(data, service_account.id)

        assert result.user_id == user.id
        assert result.created_by_service_account_id == service_account.id

    async def test_create_from_telegram_rejects_unknown_user(
        self,
        db_session: AsyncSession,
        service_account: ServiceAccountModel,
        entry_service,
    ):
        data = TelegramEntryRequestSchema(
            telegram_id="unknown",
            amount=Decimal("10.50"),
            payment_method=PaymentMethodEnum.PIX,
            category="snack",
        )
        with pytest.raises(UserNotFound):
            await entry_service.create_from_telegram(data, service_account.id)

    async def test_get_all_returns_paginated_filtered_entries(
        self,
        db_session: AsyncSession,
        user: UserModel,
        entry_service,
    ):
        EntryFactory.__async_session__ = db_session
        matching_entry = await EntryFactory.create_async(user=user, category="snack")
        await EntryFactory.create_async(user=user, category="transport")
        filters = EntryFilterSchema(
            start_date=None,
            end_date=None,
            category="snack",
            payment_method=None,
            entry_type=None,
        )
        set_params(Params(page=1, size=50))
        result = await entry_service.get_all(user.id, filters)

        assert result.total == 1
        assert [entry.id for entry in result.items] == [matching_entry.id]

    async def test_get_summary_returns_entry_aggregates(
        self,
        db_session: AsyncSession,
        user: UserModel,
        entry_service,
    ):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user=user,
            amount=Decimal("10.00"),
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        result = await entry_service.get_summary(user.id, EntrySummaryFilterSchema())

        assert result.balance == Decimal("-10.00")
        assert result.current_balance == Decimal("-10.00")
        assert result.by_entry_type[EntryTypeEnum.DEBIT] == 1
