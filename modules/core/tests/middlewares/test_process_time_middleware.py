import pytest


@pytest.mark.asyncio
class TestProcessTimeMiddleware:
    async def test_process_time_middleware(self, client):

        response = await client.get("/dummy")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
