import pytest

from modules.core.middlewares import ProcessTimeMiddleware


@pytest.mark.asyncio
class TestProcessTimeMiddleware:
    async def test_process_time_middleware(self, client_factory, app):
        app.add_middleware(ProcessTimeMiddleware)
        client = client_factory(app)

        response = client.get("/dummy")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
