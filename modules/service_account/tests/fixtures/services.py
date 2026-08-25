import pytest

from modules.core.logger import logger
from modules.service_account.repository import ServiceAccountRepository
from modules.service_account.services import ServiceAccountService


@pytest.fixture
def service_account_service(service_account_repository: ServiceAccountRepository) -> ServiceAccountService:
    return ServiceAccountService(logger, service_account_repository)
