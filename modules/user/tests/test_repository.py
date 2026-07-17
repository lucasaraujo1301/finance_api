import pytest

from modules.user.models import UserModel
from modules.user.repository import UserRepository


@pytest.mark.asyncio(loop_scope="session")
class TestUserRepository:
    async def test_create_persists_user_and_assigns_id(self, db_session):
        repo = UserRepository(db_session)
        user = UserModel(full_name="Alice", telegram_id="111", api_key="fin_key_1")

        result = await repo.create(user)

        assert result.id is not None
        assert result.full_name == "Alice"
        assert result.telegram_id == "111"
        assert result.api_key == "fin_key_1"

    async def test_get_user_by_api_key_returns_user_when_found(self, db_session):
        repo = UserRepository(db_session)
        user = UserModel(full_name="Bob", telegram_id="222", api_key="fin_key_2")
        await repo.create(user)

        found = await repo.get_user_by_api_key("fin_key_2")

        assert found is not None
        assert found.id == user.id
        assert found.full_name == "Bob"

    async def test_get_user_by_api_key_returns_none_when_not_found(self, db_session):
        repo = UserRepository(db_session)

        found = await repo.get_user_by_api_key("nonexistent_key")

        assert found is None

    async def test_get_user_by_telegram_id_returns_user_when_found(self, db_session):
        repo = UserRepository(db_session)
        user = UserModel(full_name="Charlie", telegram_id="333", api_key="fin_key_3")
        await repo.create(user)

        found = await repo.get_user_by_telegram_id("333")

        assert found is not None
        assert found.id == user.id
        assert found.telegram_id == "333"

    async def test_get_user_by_telegram_id_returns_none_when_not_found(self, db_session):
        repo = UserRepository(db_session)

        found = await repo.get_user_by_telegram_id("999")

        assert found is None
