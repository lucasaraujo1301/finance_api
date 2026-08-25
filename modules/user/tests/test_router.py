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
            json={
                "full_name": "alice",
                "email": "alice@example.com",
                "telegram_id": "111",
                "password": "secret-password",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["success"] is True
        assert response.json()["data"]["full_name"] == "alice"
        assert response.json()["data"]["telegram_id"] == "111"
        assert "password" not in response.json()["data"]

    async def test_create_duplicate_telegram_id_returns_400(self, client, admin_user, user):
        response = await self.auth_post(
            client,
            admin_user,
            path="/",
            json={
                "full_name": "Test API",
                "email": "duplicate@example.com",
                "telegram_id": user.telegram_id,
                "password": "secret-password",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["success"] is False
        assert response.json()["errors"]["message"] == UserAlreadyExistException.message

    async def test_create_user_requires_superuser(self, client, user):
        response = await self.auth_post(
            client,
            user,
            path="/",
            json={
                "full_name": "alice",
                "email": "alice@example.com",
                "telegram_id": "111",
                "password": "secret-password",
            },
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["success"] is False
        assert response.json()["errors"]["message"] == SuperuserRequired.message

    async def test_create_telegram_user_with_service_account(self, client, service_account_with_api_key):
        _, raw_key = service_account_with_api_key

        response = await self.auth_post(
            client,
            path="/telegram",
            headers={"X-API-KEY": raw_key},
            json={"full_name": "Telegram User", "email": "telegram@example.com", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["success"] is True
        assert response.json()["data"]["full_name"] == "Telegram User"
        assert response.json()["data"]["telegram_id"] == "222"
        assert response.json()["data"]["password_update_url"].startswith("http://localhost:3000/reset-password?token=")
        assert "password" not in response.json()["data"]

    async def test_create_telegram_user_requires_service_account(self, client):
        response = await self.auth_post(
            client,
            path="/telegram",
            headers=None,
            json={"full_name": "Telegram User", "email": "telegram@example.com", "telegram_id": "222"},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["success"] is False
        assert response.json()["errors"]["message"] == ApiKeyMissing.message

    async def test_me(self, client, user):
        response = await self.auth_get(client, user, path="/me")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"]["id"] == str(user.id)

    async def test_update_me(self, client, user):
        response = await self.auth_patch(
            client,
            user,
            path="/me",
            json={"full_name": "Updated Name", "password": "new-secret-password"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["success"] is True
        assert response.json()["data"]["id"] == str(user.id)
        assert response.json()["data"]["full_name"] == "Updated Name"
        assert user.full_name == "Updated Name"
        assert user.password != "new-secret-password"

    async def test_update_me_requires_authentication(self, client):
        response = await client.patch(f"{self.base_url}/me", json={"full_name": "Updated Name"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
class TestAuthRouter:
    base_url = "/api/v1/auth"

    async def test_login_and_refresh(self, client, user_with_password):
        user, password = user_with_password

        login_response = await client.post(
            f"{self.base_url}/login",
            json={"email": user.email, "password": password},
        )

        assert login_response.status_code == status.HTTP_200_OK
        assert login_response.json()["success"] is True
        assert login_response.json()["data"]["full_name"] == user.full_name
        assert login_response.json()["data"]["is_superuser"] is user.is_superuser
        assert "password_update_token" not in login_response.json()["data"]

        refresh_response = await client.post(
            f"{self.base_url}/refresh",
            json={"refresh_token": login_response.json()["data"]["refresh_token"]},
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        assert refresh_response.json()["success"] is True
        assert refresh_response.json()["data"]["access_token"]
        assert refresh_response.json()["data"]["refresh_token"]

    async def test_password_setup_token_updates_password_once(
        self,
        client,
        db_session,
        user_with_password,
        auth_service,
    ):
        user, _ = user_with_password
        user.needs_password_update = True
        await db_session.flush()

        setup_token = auth_service.create_password_update_url(user).split("token=", 1)[1]

        response = await client.patch(
            "/api/v1/users/password",
            headers={"Authorization": f"Bearer {setup_token}"},
            json={"password": "new-password"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert user.needs_password_update is False

        replay_response = await client.patch(
            "/api/v1/users/password",
            headers={"Authorization": f"Bearer {setup_token}"},
            json={"password": "another-password"},
        )

        assert replay_response.status_code == status.HTTP_401_UNAUTHORIZED
