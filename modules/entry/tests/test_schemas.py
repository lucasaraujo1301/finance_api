from datetime import date, timedelta
from decimal import Decimal

import pytest

from pydantic import ValidationError

from modules.entry.enums import PaymentMethodEnum
from modules.entry.schemas import EntryRequestSchema


@pytest.mark.parametrize("payment_date", [date.today(), date.today() - timedelta(days=1)])
def test_entry_request_accepts_current_and_past_payment_dates(payment_date: date):
    entry = EntryRequestSchema(
        amount=Decimal("10.00"),
        payment_method=PaymentMethodEnum.PIX,
        category="Food",
        payment_date=payment_date,
    )

    assert entry.payment_date == payment_date


def test_entry_request_rejects_future_payment_date():
    with pytest.raises(ValidationError, match="payment_date cannot be in the future"):
        EntryRequestSchema(
            amount=Decimal("10.00"),
            payment_method=PaymentMethodEnum.PIX,
            category="Food",
            payment_date=date.today() + timedelta(days=1),
        )
