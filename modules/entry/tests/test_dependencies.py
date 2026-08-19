import pytest

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.entry.dependencies import get_entry_service
from modules.entry.services import EntryService
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
async def test_get_entry_service_returns_configured_service(db_session: AsyncSession):
    user_service = UserService(logger, db_session, PasswordHash.recommended())

    service = get_entry_service(db_session, user_service)

    assert isinstance(service, EntryService)
    assert service.logger is logger
    assert service._entry_repository._session is db_session
    assert service._user_service is user_service
