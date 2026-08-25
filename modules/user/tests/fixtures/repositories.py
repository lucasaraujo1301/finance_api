import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.repository import UserRepository


@pytest.fixture
def user_repository(db_session: AsyncSession) -> UserRepository:
    return UserRepository(db_session)
