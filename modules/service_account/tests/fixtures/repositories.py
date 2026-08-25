import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.service_account.repository import ServiceAccountRepository


@pytest.fixture
def service_account_repository(db_session: AsyncSession) -> ServiceAccountRepository:
    return ServiceAccountRepository(db_session)
