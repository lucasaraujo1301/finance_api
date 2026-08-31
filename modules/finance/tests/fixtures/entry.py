import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from modules.finance.models import EntryModel
from modules.finance.tests.fixtures.factories import EntryFactory
from modules.user.models import UserModel


@pytest_asyncio.fixture(scope="function")
async def entry(db_session: AsyncSession, user: UserModel) -> EntryModel:
    EntryFactory.__async_session__ = db_session

    entry = await EntryFactory.create_async(user_id=user.id)

    await db_session.flush()

    return entry
