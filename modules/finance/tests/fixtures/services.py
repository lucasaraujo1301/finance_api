import pytest

from modules.core.logger import logger
from modules.finance.repository import EntryRepository
from modules.finance.services import EntryService
from modules.user.services import UserService


@pytest.fixture
def entry_service(entry_repository: EntryRepository, user_service: UserService) -> EntryService:
    return EntryService(logger, entry_repository, user_service)
