from datetime import date
from decimal import Decimal

import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel
from modules.entry.schemas import EntryRequestSchema
from modules.entry.services import EntryService
from modules.user.models import UserModel


@pytest.mark.asyncio(loop_scope="session")
class TestEntryService:
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
        service = EntryService(logger, db_session)

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
