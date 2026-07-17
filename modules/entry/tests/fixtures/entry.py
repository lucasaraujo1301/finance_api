import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from modules.entry.models import EntryModel
from modules.entry.tests.fixtures.factories import EntryFactory
from modules.user.models import UserModel


@pytest_asyncio.fixture(scope="function")
async def entry(db_session: AsyncSession, user: UserModel) -> EntryModel:
    EntryFactory.__async_session__ = db_session

    entry = await EntryFactory.create_async(user=user)

    await db_session.flush()

    return entry
