import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.models import UserModel
from modules.user.tests.fixtures.factories import UserFactory


@pytest_asyncio.fixture(scope="function")
async def user_with_api_key(db_session: AsyncSession) -> tuple[UserModel, str]:
    UserFactory.__async_session__ = db_session
    raw_key, encrypted_key = UserFactory.api_key_pair()

    return await UserFactory.create_async(api_key=encrypted_key), raw_key


@pytest_asyncio.fixture(scope="function")
async def user(db_session: AsyncSession) -> UserModel:
    UserFactory.__async_session__ = db_session

    return await UserFactory.create_async()
