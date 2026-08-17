import pytest

from pydantic import ValidationError

from modules.service_account.schemas import CreateServiceAccountSchema


def test_create_service_account_accepts_name():
    schema = CreateServiceAccountSchema(name="telegram-bot")

    assert schema.name == "telegram-bot"


@pytest.mark.parametrize("name", ["", "a" * 256])
def test_create_service_account_rejects_invalid_name(name: str):
    with pytest.raises(ValidationError):
        CreateServiceAccountSchema(name=name)
