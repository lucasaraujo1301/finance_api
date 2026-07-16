from decimal import Decimal

import pytest

from pydantic import TypeAdapter, ValidationError

from modules.core.types import Money

money_adapter = TypeAdapter(Money)


def test_money_converts_string_to_decimal():
    assert money_adapter.validate_python("10.50") == Decimal("10.50")


@pytest.mark.parametrize("value", ["0", "-1.00", "1.234", "12345678901.23"])
def test_money_rejects_values_outside_constraints(value: str):
    with pytest.raises(ValidationError):
        money_adapter.validate_python(value)


def test_money_preserves_decimal_in_python_serialization():
    value = Decimal("10.50")

    assert money_adapter.dump_python(value) == value


def test_money_serializes_as_string_in_json():
    assert money_adapter.dump_json(Decimal("10.50")) == b'"10.50"'
