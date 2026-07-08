import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.models import User
from modules.user.tests.fixtures.factories import UserFactory


@pytest_asyncio.fixture(scope="function")
async def user(db_session: AsyncSession) -> User:
    UserFactory.__async_session__ = db_session

    return await UserFactory.create_async()
