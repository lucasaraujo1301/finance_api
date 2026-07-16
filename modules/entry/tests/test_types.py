import pytest

from pydantic import TypeAdapter, ValidationError

from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.types import EntryType, PaymentMethod

entry_type_adapter = TypeAdapter(EntryType)
payment_method_adapter = TypeAdapter(PaymentMethod)


@pytest.mark.parametrize("entry_type", list(EntryTypeEnum))
def test_entry_type_converts_value_to_enum(entry_type: EntryTypeEnum):
    assert entry_type_adapter.validate_python(entry_type.value) is entry_type


@pytest.mark.parametrize("entry_type", list(EntryTypeEnum))
def test_entry_type_serialization(entry_type: EntryTypeEnum):
    assert entry_type_adapter.dump_python(entry_type) is entry_type
    assert entry_type_adapter.dump_json(entry_type) == f'"{entry_type.value.title()}"'.encode()


@pytest.mark.parametrize("payment_method", list(PaymentMethodEnum))
def test_payment_method_converts_value_to_enum(payment_method: PaymentMethodEnum):
    assert payment_method_adapter.validate_python(payment_method.value) is payment_method


@pytest.mark.parametrize("payment_method", list(PaymentMethodEnum))
def test_payment_method_serialization(payment_method: PaymentMethodEnum):
    expected = payment_method.value.replace("_", " ").title()

    assert payment_method_adapter.dump_python(payment_method) is payment_method
    assert payment_method_adapter.dump_json(payment_method) == f'"{expected}"'.encode()


@pytest.mark.parametrize("adapter", [entry_type_adapter, payment_method_adapter])
def test_enum_type_rejects_unknown_value(adapter: TypeAdapter):
    with pytest.raises(ValidationError):
        adapter.validate_python("unknown")
