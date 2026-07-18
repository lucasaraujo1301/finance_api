import pytest

from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

from modules.core.expcetion import BaseException, Modules, SystemException
from modules.core.handlers import register_exception_handlers


class SomeException(BaseException):
    module = Modules.system


@pytest.mark.asyncio
class TestExceptionHandlers:
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        register_exception_handlers(test_app)

        @test_app.get("/server_error")
        async def server_error():
            raise RuntimeError("Unexpected")

        @test_app.get("/validation_error")
        async def validation_error():
            raise RequestValidationError(
                [{"loc": ("body", "x"), "msg": "field required", "type": "value_error.missing"}]
            )

        @test_app.get("/base_exception")
        async def base_exception():
            raise SomeException()

        @test_app.get("/integrity_error")
        async def integrity_error():
            raise IntegrityError("INSERT INTO ...", {}, Exception("duplicate key"))

    async def test_returns_success_true_for_normal_response(self, client_factory, test_app):
        async with client_factory(test_app) as client:
            response = await client.get("/dummy")
            assert response.status_code == 200
            assert response.json() == {"message": "Hello!"}

    async def test_validation_error_returns_422_with_errors(self, client_factory, test_app):
        async with client_factory(test_app) as client:
            response = await client.get("/validation_error")
            assert response.status_code == 422
            body = response.json()
            assert body["success"] is False
            assert isinstance(body["error"], list)

    async def test_integrity_error_returns_409(self, client_factory, test_app):
        async with client_factory(test_app) as client:
            response = await client.get("/integrity_error")
            assert response.status_code == 409
            assert response.json() == {"success": False, "error": "Integrity error occurred"}

    async def test_unhandled_exception_returns_500(self, client_factory, test_app):
        async with client_factory(test_app, raise_server_exceptions=False) as client:
            response = await client.get("/server_error")
            assert response.status_code == 500
            assert response.json() == {
                "success": False,
                "error": {"code": SystemException().error_code, "message": SystemException.message},
            }

    async def test_base_exception_handler(self, client_factory, test_app):
        expect = {"success": False, "error": {"code": SomeException().error_code, "message": SomeException.message}}
        async with client_factory(test_app, raise_server_exceptions=False) as client:
            response = await client.get("/base_exception")
            assert response.status_code == SomeException.status_code
            assert response.json() == expect
