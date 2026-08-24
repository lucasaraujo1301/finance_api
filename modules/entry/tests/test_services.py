from datetime import date
from decimal import Decimal

import pytest

from fastapi_pagination import Params
from fastapi_pagination.api import set_params
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema, TelegramEntryRequestSchema
from modules.entry.services import EntryService
from modules.entry.tests.fixtures.factories import EntryFactory
from modules.service_account.models import ServiceAccountModel
from modules.user.exceptions import UserNotFound
from modules.user.models import UserModel
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestEntryService:
    def _get_service(self, db_session: AsyncSession) -> EntryService:
        user_service = UserService(logger, db_session, PasswordHash.recommended())
        return EntryService(logger, db_session, user_service)

    async def test_create_persists_and_returns_entry(self, db_session: AsyncSession, user: UserModel):
        payment_date = date.today()
        data = EntryRequestSchema(
            amount=Decimal("10.50"),
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
            category="food",
            description="Lunch",
            payment_date=payment_date,
            is_fixed=False,
        )
        service = self._get_service(db_session)

        result = await service.create(user.id, data)

        persisted = await db_session.get(EntryModel, result.id)
        assert persisted is not None
        assert persisted.id == result.id
        assert result.user_id == user.id
        assert result.amount == Decimal("10.50")
        assert result.entry_type == EntryTypeEnum.DEBIT
        assert result.payment_method == PaymentMethodEnum.PIX
        assert result.category == "food"
        assert result.description == "Lunch"
        assert result.payment_date == payment_date
        assert result.is_fixed is False

    async def test_create_from_telegram_validates_user_and_delegates_creation(
        self,
        db_session: AsyncSession,
        user: UserModel,
        service_account: ServiceAccountModel,
    ):
        data = TelegramEntryRequestSchema(
            telegram_id=user.telegram_id,
            amount=Decimal("10.50"),
            payment_method=PaymentMethodEnum.PIX,
            category="food",
        )
        service = self._get_service(db_session)

        result = await service.create_from_telegram(data, service_account.id)

        assert result.user_id == user.id
        assert result.created_by_service_account_id == service_account.id

    async def test_create_from_telegram_rejects_unknown_user(
        self,
        db_session: AsyncSession,
        service_account: ServiceAccountModel,
    ):
        data = TelegramEntryRequestSchema(
            telegram_id="unknown",
            amount=Decimal("10.50"),
            payment_method=PaymentMethodEnum.PIX,
            category="food",
        )
        service = self._get_service(db_session)

        with pytest.raises(UserNotFound):
            await service.create_from_telegram(data, service_account.id)

    async def test_get_all_returns_paginated_filtered_entries(self, db_session: AsyncSession, user: UserModel):
        EntryFactory.__async_session__ = db_session
        matching_entry = await EntryFactory.create_async(user=user, category="food")
        await EntryFactory.create_async(user=user, category="transport")
        filters = EntryFilterSchema(
            start_date=None,
            end_date=None,
            category="food",
            payment_method=None,
            entry_type=None,
        )
        set_params(Params(page=1, size=50))
        service = self._get_service(db_session)

        result = await service.get_all(user.id, filters)

        assert result.total == 1
        assert [entry.id for entry in result.items] == [matching_entry.id]

    async def test_get_summary_returns_entry_aggregates(self, db_session: AsyncSession, user: UserModel):
        EntryFactory.__async_session__ = db_session
        await EntryFactory.create_async(
            user=user,
            amount=Decimal("10.00"),
            entry_type=EntryTypeEnum.DEBIT,
            payment_method=PaymentMethodEnum.PIX,
        )
        service = self._get_service(db_session)

        result = await service.get_summary(user.id, EntryFilterSchema())

        assert result.balance == Decimal("-10.00")
        assert result.current_balance == Decimal("-10.00")
        assert result.by_entry_type[EntryTypeEnum.DEBIT] == 1
