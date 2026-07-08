from unittest.mock import patch

import pytest

from modules.user.schemas import CreateUserSchema
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserService:
    RAW_KEY = "fin_test_raw_key_abc123"
    ENCRYPTED_KEY = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_persists_user_and_returns_raw_api_key(
        self, mock_generate_api_key, db_session
    ):
        data = CreateUserSchema(full_name="Alice", telegram_id="111")
        service = UserService(db_session)

        result = await service.create_user(data)

        assert result["full_name"] == "Alice"
        assert result["telegram_id"] == "111"
        assert result["api_key"] == self.RAW_KEY
        assert "id" in result

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_stores_encrypted_key_in_database(
        self, mock_generate_api_key, db_session
    ):
        data = CreateUserSchema(full_name="Bob", telegram_id="222")
        service = UserService(db_session)

        result = await service.create_user(data)

        from sqlalchemy import select
        from modules.user.models import User

        cursor = await db_session.execute(select(User).where(User.id == result["id"]))
        persisted = cursor.scalars().first()
        assert persisted is not None
        assert persisted.api_key == self.ENCRYPTED_KEY
        assert persisted.api_key != result["api_key"]

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_without_full_name(
        self, mock_generate_api_key, db_session
    ):
        data = CreateUserSchema(telegram_id="333")
        service = UserService(db_session)

        result = await service.create_user(data)

        assert result["full_name"] is None
        assert result["telegram_id"] == "333"
        assert result["api_key"] == self.RAW_KEY
