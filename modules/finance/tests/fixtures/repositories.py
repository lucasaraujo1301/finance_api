import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.finance.repository import EntryRepository


@pytest.fixture
def entry_repository(db_session: AsyncSession) -> EntryRepository:
    return EntryRepository(db_session)
