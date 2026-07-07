import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()

    @app.get("/dummy")
    async def dummy_route():
        return {"message": "I am a temporary test route"}

    return app

@pytest.fixture
def client_factory():
    def _client_factory(app: FastAPI) -> TestClient:
        return TestClient(app)
    return _client_factory
