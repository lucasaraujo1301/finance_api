import pytest

from modules.core.logger import logger
from modules.service_account.dependencies import get_current_service_account
from modules.service_account.exceptions import ApiKeyMissing
from modules.service_account.services import ServiceAccountService


@pytest.mark.asyncio(loop_scope="session")
class TestServiceAccountDependencies:
    async def test_get_current_service_account_returns_account(self, db_session, service_account_with_api_key):
        service_account, raw_key = service_account_with_api_key
        service = ServiceAccountService(logger, db_session)

        result = await get_current_service_account(api_key=raw_key, service=service)

        assert result.id == service_account.id

    async def test_get_current_service_account_raises_when_api_key_missing(self, db_session):
        service = ServiceAccountService(logger, db_session)

        with pytest.raises(ApiKeyMissing):
            await get_current_service_account(api_key=None, service=service)
