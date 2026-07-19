import pytest

from fastapi import status


@pytest.mark.asyncio
class TestLocaleMiddleware:
    @pytest.mark.parametrize(("locate", "expected_message"), [("en", "Hello!"), ("pt-BR", "Olá!"), ("es", "¡Hola!")])
    async def test_locale_middleware(self, locate, expected_message, client):
        headers = {"Accept-Language": locate}

        response = await client.get("/dummy", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == expected_message
