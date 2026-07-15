from typing import AsyncGenerator

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from modules.core.config import settings
from modules.core.models import Base


@pytest_asyncio.fixture(scope="session", autouse=True)
async def test_engine():
    engine = create_async_engine(settings.database_test_url, echo=False, poolclass=NullPool)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine  # Passa o engine para ser usado pelas outras fixtures

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def test_session_maker(test_engine):
    """Cria a fábrica de sessões compartilhada."""
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine, test_session_maker) -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.connect() as connection:
        await connection.begin()

        async with test_session_maker(bind=connection) as session:
            yield session
