import pytest

from modules.service_account.dependencies import get_current_service_account
from modules.service_account.exceptions import ApiKeyMissing


@pytest.mark.asyncio(loop_scope="session")
class TestServiceAccountDependencies:
    async def test_get_current_service_account_returns_account(
        self,
        service_account_with_api_key,
        service_account_service,
    ):
        service_account, raw_key = service_account_with_api_key

        result = await get_current_service_account(api_key=raw_key, service=service_account_service)

        assert result.id == service_account.id

    async def test_get_current_service_account_raises_when_api_key_missing(self, service_account_service):
        with pytest.raises(ApiKeyMissing):
            await get_current_service_account(api_key=None, service=service_account_service)
