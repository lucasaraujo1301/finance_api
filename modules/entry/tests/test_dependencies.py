import pytest

from modules.core.logger import logger
from modules.entry.dependencies import get_entry_service
from modules.entry.services import EntryService


@pytest.mark.asyncio(loop_scope="session")
async def test_get_entry_service_returns_configured_service(
    entry_repository,
    user_service,
):
    service = get_entry_service(entry_repository, user_service)

    assert isinstance(service, EntryService)
    assert service.logger is logger
    assert service._entry_repository is entry_repository
    assert service._user_service is user_service
