import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from modules.service_account.models import ServiceAccountModel
from modules.service_account.tests.fixtures.factories import ServiceAccountFactory


@pytest_asyncio.fixture(scope="function")
async def service_account(db_session: AsyncSession) -> ServiceAccountModel:
    ServiceAccountFactory.__async_session__ = db_session
    return await ServiceAccountFactory.create_async()


@pytest_asyncio.fixture(scope="function")
async def service_account_with_api_key(db_session: AsyncSession) -> tuple[ServiceAccountModel, str]:
    ServiceAccountFactory.__async_session__ = db_session
    raw_key, encrypted_key = ServiceAccountFactory.api_key_pair()
    service_account = await ServiceAccountFactory.create_async(api_key=encrypted_key)
    return service_account, raw_key
