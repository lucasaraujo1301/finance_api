import pytest

from httpx import ASGITransport, AsyncClient
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, SQLAlchemyPersistenceMethod, T


@pytest.fixture
def client_factory():
    def _create_client(app, raise_server_exceptions=True):
        transport = ASGITransport(app=app, raise_app_exceptions=raise_server_exceptions)

        return AsyncClient(transport=transport, base_url="http://test")

    return _create_client


class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __set_relationships__ = True
    __persistence_method__ = SQLAlchemyPersistenceMethod.FLUSH

    updated_at = None
    deleted_at = None
