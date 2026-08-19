import pytest

from fastapi import status


@pytest.mark.asyncio(loop_scope="session")
class TestUserRouter:
    base_url = "/api/v1/users/"

    async def test_create_user_persists_in_database(self, client):
        response = await client.post(
            self.base_url,
            json={"full_name": "alice", "telegram_id": "111", "password": "secret-password"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["full_name"] == "alice"
        assert response.json()["telegram_id"] == "111"
        assert "password" not in response.json()

    async def test_create_duplicate_telegram_id_returns_400(self, client, user):
        response = await client.post(
            self.base_url,
            json={"full_name": "Test API", "telegram_id": user.telegram_id, "password": "secret-password"},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_create_telegram_user_with_service_account(self, client, service_account_with_api_key):
        _, raw_key = service_account_with_api_key

        response = await client.post(
            f"{self.base_url}telegram/",
            headers={"X-API-KEY": raw_key},
            json={"full_name": "Telegram User", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["full_name"] == "Telegram User"
        assert response.json()["telegram_id"] == "222"
        assert "password" not in response.json()

    async def test_create_telegram_user_requires_service_account(self, client):
        response = await client.post(
            f"{self.base_url}telegram/",
            json={"full_name": "Telegram User", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


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
