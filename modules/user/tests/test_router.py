import pytest

from fastapi import status

from modules.service_account.exceptions import ApiKeyMissing
from modules.user.exceptions import SuperuserRequired, UserAlreadyExistException
from modules.user.tests.mixin import AuthRequestMixin


@pytest.mark.asyncio(loop_scope="session")
class TestUserRouter(AuthRequestMixin):
    base_url = "/api/v1/users"

    async def test_create_user_persists_in_database(self, client, admin_user):
        response = await self.auth_post(
            client,
            admin_user,
            path="/",
            json={"full_name": "alice", "telegram_id": "111", "password": "secret-password"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["full_name"] == "alice"
        assert response.json()["telegram_id"] == "111"
        assert "password" not in response.json()

    async def test_create_duplicate_telegram_id_returns_400(self, client, admin_user, user):
        response = await self.auth_post(
            client,
            admin_user,
            path="/",
            json={"full_name": "Test API", "telegram_id": user.telegram_id, "password": "secret-password"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["success"] is False
        assert response.json()["error"]["message"] == UserAlreadyExistException.message

    async def test_create_user_requires_superuser(self, client, user):
        response = await self.auth_post(
            client,
            user,
            path="/",
            json={"full_name": "alice", "telegram_id": "111", "password": "secret-password"},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["success"] is False
        assert response.json()["error"]["message"] == SuperuserRequired.message

    async def test_create_telegram_user_with_service_account(self, client, service_account_with_api_key):
        _, raw_key = service_account_with_api_key

        response = await self.auth_post(
            client,
            path="/telegram",
            headers={"X-API-KEY": raw_key},
            json={"full_name": "Telegram User", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["full_name"] == "Telegram User"
        assert response.json()["telegram_id"] == "222"
        assert "password" not in response.json()

    async def test_create_telegram_user_requires_service_account(self, client):
        response = await self.auth_post(
            client,
            path="/telegram",
            headers=None,
            json={"full_name": "Telegram User", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["success"] is False
        assert response.json()["error"]["message"] == ApiKeyMissing.message


@pytest.mark.asyncio(loop_scope="session")
class TestAuthRouter:
    base_url = "/api/v1/auth"

    async def test_login_and_refresh(self, client, user_with_password):
        user, password = user_with_password

        login_response = await client.post(
            f"{self.base_url}/login",
            json={"telegram_id": user.telegram_id, "password": password},
        )

        assert login_response.status_code == status.HTTP_200_OK
        assert login_response.json()["full_name"] == user.full_name
        assert login_response.json()["is_superuser"] is user.is_superuser

        refresh_response = await client.post(
            f"{self.base_url}/refresh",
            json={"refresh_token": login_response.json()["refresh_token"]},
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        assert refresh_response.json()["access_token"]
        assert refresh_response.json()["refresh_token"]
