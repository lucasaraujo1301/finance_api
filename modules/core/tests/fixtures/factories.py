import pytest

from httpx import ASGITransport, AsyncClient


@pytest.fixture
def client_factory():
    def _create_client(app, raise_server_exceptions=True):
        transport = ASGITransport(app=app, raise_app_exceptions=raise_server_exceptions)

        return AsyncClient(transport=transport, base_url="http://test")

    return _create_client
