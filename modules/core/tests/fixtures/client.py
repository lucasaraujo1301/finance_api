from typing import AsyncGenerator

import pytest
import pytest_asyncio

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.database import get_db
from modules.core.handlers import register_exception_handlers
from modules.core.main import app as main_app
from modules.core.middlewares import ProcessTimeMiddleware


@pytest.fixture
def test_app() -> FastAPI:
    app_copy = FastAPI()

    app_copy.include_router(main_app.router)

    register_exception_handlers(app_copy)
    app_copy.add_middleware(ProcessTimeMiddleware)

    @app_copy.get("/dummy")
    async def dummy_route():
        return {"message": "I am a temporary test route"}

    return app_copy


@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI, db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Generates an AsyncClient that overrides the main app's session dependency."""

    async def _override_get_async_session():
        yield db_session

    # Intercept original dependency mapping
    test_app.dependency_overrides[get_db] = _override_get_async_session

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    test_app.dependency_overrides.clear()
