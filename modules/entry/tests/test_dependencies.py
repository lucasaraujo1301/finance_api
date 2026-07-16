import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.entry.dependencies import get_entry_service
from modules.entry.services import EntryService


@pytest.mark.asyncio(loop_scope="session")
async def test_get_entry_service_returns_configured_service(db_session: AsyncSession):
    service = get_entry_service(db_session)

    assert isinstance(service, EntryService)
    assert service.logger is logger
    assert service._entry_repository._session is db_session
