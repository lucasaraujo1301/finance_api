import pytest

from modules.user.models import UserModel
from modules.user.repository import UserRepository


@pytest.mark.asyncio(loop_scope="session")
class TestUserRepository:
    async def test_create_persists_user_and_assigns_id(self, db_session):
        repo = UserRepository(db_session)
        user = UserModel(full_name="Alice", email="alice@example.com", telegram_id="111", password="$argon2id$hash")

        result = await repo.create(user)

        assert result.id is not None
        assert result.full_name == "Alice"
        assert result.telegram_id == "111"

    async def test_get_user_by_telegram_id_returns_user_when_found(self, db_session, user):
        repo = UserRepository(db_session)

        found = await repo.get_user_by_telegram_id(user.telegram_id)

        assert found is not None
        assert found.id == user.id
        assert found.telegram_id == user.telegram_id

    async def test_get_user_by_telegram_id_returns_none_when_not_found(self, db_session):
        repo = UserRepository(db_session)

        found = await repo.get_user_by_telegram_id("999")

        assert found is None

    async def test_get_user_by_email_returns_user_when_found(self, db_session, user):
        repo = UserRepository(db_session)

        found = await repo.get_user_by_email(user.email)

        assert found is not None
        assert found.id == user.id
