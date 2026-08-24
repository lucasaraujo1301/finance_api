from datetime import date, timedelta
from decimal import Decimal

import pytest

from pydantic import ValidationError

from modules.entry.enums import PaymentMethodEnum
from modules.entry.schemas import EntryFilterSchema, EntryRequestSchema


@pytest.mark.parametrize("payment_date", [date.today(), date.today() - timedelta(days=1)])
def test_entry_request_accepts_current_and_past_payment_dates(payment_date: date):
    entry = EntryRequestSchema(
        amount=Decimal("10.00"),
        payment_method=PaymentMethodEnum.PIX,
        category="snack",
        payment_date=payment_date,
    )

    assert entry.payment_date == payment_date


def test_entry_request_rejects_future_payment_date():
    with pytest.raises(ValidationError, match="payment_date cannot be in the future"):
        EntryRequestSchema(
            amount=Decimal("10.00"),
            payment_method=PaymentMethodEnum.PIX,
            category="snack",
            payment_date=date.today() + timedelta(days=1),
        )


@pytest.mark.parametrize("end_date_offset", [0, -1])
def test_entry_filter_requires_end_date_after_start_date(end_date_offset: int):
    start_date = date.today()

    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        EntryFilterSchema(
            start_date=start_date,
            end_date=start_date + timedelta(days=end_date_offset),
        )
