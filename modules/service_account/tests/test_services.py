from unittest.mock import patch

import pytest

from sqlalchemy import select

from modules.core.logger import logger
from modules.service_account.exceptions import ServiceAccountAlreadyExists, ServiceAccountNotFound
from modules.service_account.models import ServiceAccountModel
from modules.service_account.schemas import CreateServiceAccountSchema
from modules.service_account.services import ServiceAccountService


@pytest.mark.asyncio(loop_scope="session")
class TestServiceAccountService:
    raw_key = "fin_test_raw_key"
    encrypted_key = "a" * 64

    @patch(
        "modules.service_account.services.generate_api_key",
        return_value=(raw_key, encrypted_key),
    )
    async def test_create_persists_encrypted_key_and_returns_raw_key(self, generate_api_key_mock, db_session):
        service = ServiceAccountService(logger, db_session)

        result = await service.create(CreateServiceAccountSchema(name="telegram-bot"))

        persisted = await db_session.scalar(select(ServiceAccountModel).where(ServiceAccountModel.id == result.id))
        assert result.name == "telegram-bot"
        assert result.api_key == self.raw_key
        assert persisted is not None
        assert persisted.api_key == self.encrypted_key
        generate_api_key_mock.assert_called_once_with()

    async def test_create_rejects_existing_name_even_when_deleted(self, db_session, service_account):
        service = ServiceAccountService(logger, db_session)
        service_account.deleted_at = service_account.created_at
        await db_session.flush()

        with pytest.raises(ServiceAccountAlreadyExists):
            await service.create(CreateServiceAccountSchema(name=service_account.name))

    async def test_get_by_api_key_returns_service_account(self, db_session, service_account_with_api_key):
        service_account, raw_key = service_account_with_api_key
        service = ServiceAccountService(logger, db_session)

        result = await service.get_by_api_key(raw_key)

        assert result.id == service_account.id

    async def test_get_by_api_key_raises_when_not_found(self, db_session):
        service = ServiceAccountService(logger, db_session)

        with pytest.raises(ServiceAccountNotFound):
            await service.get_by_api_key(self.raw_key)
