import pytest_asyncio

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.models import UserModel
from modules.user.tests.fixtures.factories import UserFactory


@pytest_asyncio.fixture(scope="function")
async def user(db_session: AsyncSession) -> UserModel:
    UserFactory.__async_session__ = db_session

    return await UserFactory.create_async()


@pytest_asyncio.fixture(scope="function")
async def user_with_password(db_session: AsyncSession) -> tuple[UserModel, str]:
    password = "secret-password"
    UserFactory.__async_session__ = db_session
    user = await UserFactory.create_async(password=PasswordHash.recommended().hash(password))
    return user, password
