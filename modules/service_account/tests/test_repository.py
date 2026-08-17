import pytest

from modules.service_account.models import ServiceAccountModel
from modules.service_account.repository import ServiceAccountRepository


@pytest.mark.asyncio(loop_scope="session")
class TestServiceAccountRepository:
    async def test_create_persists_service_account(self, db_session):
        repository = ServiceAccountRepository(db_session)

        result = await repository.create(ServiceAccountModel(name="telegram-bot", api_key="encrypted-key"))

        assert result.id is not None
        assert result.name == "telegram-bot"
        assert result.api_key == "encrypted-key"

    async def test_get_by_name_returns_deleted_service_account(self, db_session, service_account):
        repository = ServiceAccountRepository(db_session)
        await repository.delete(service_account)

        result = await repository.get_by_name(service_account.name)

        assert result is not None
        assert result.id == service_account.id

    async def test_get_by_name_returns_none_when_not_found(self, db_session):
        repository = ServiceAccountRepository(db_session)

        assert await repository.get_by_name("missing") is None

    async def test_get_by_api_key_returns_active_service_account(self, db_session, service_account):
        repository = ServiceAccountRepository(db_session)

        result = await repository.get_by_api_key(service_account.api_key)

        assert result is not None
        assert result.id == service_account.id

    async def test_get_by_api_key_ignores_deleted_service_account(self, db_session, service_account):
        repository = ServiceAccountRepository(db_session)
        await repository.delete(service_account)

        assert await repository.get_by_api_key(service_account.api_key) is None
