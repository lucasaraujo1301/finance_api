import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestUserRouter:
    base_url = "/api/v1/users/"

    async def test_create_user_persists_in_database(self, client):
        response = await client.post(self.base_url, json={"full_name": "alice", "telegram_id": "111"})
        assert response.status_code == 201
        assert response.json()["api_key"].startswith("fin_")

    async def test_create_duplicate_telegram_id_returns_400(self, client, user):
        response = await client.post(self.base_url, json={"full_name": "Test API", "telegram_id": user.telegram_id})
        assert response.status_code == 409
