from unittest.mock import patch

import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import User
from modules.user.schemas import CreateUserSchema
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserService:
    RAW_KEY = "fin_test_raw_key_abc123"
    ENCRYPTED_KEY = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_persists_user_and_returns_raw_api_key(
        self, mock_generate_api_key, db_session: AsyncSession
    ):
        data = CreateUserSchema(full_name="Alice", telegram_id="111")
        service = UserService(db_session)

        result = await service.create_user(data)

        assert result["full_name"] == "Alice"
        assert result["telegram_id"] == "111"
        assert result["api_key"] == self.RAW_KEY
        assert "id" in result

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_stores_encrypted_key_in_database(self, mock_generate_api_key, db_session: AsyncSession):
        data = CreateUserSchema(full_name="Bob", telegram_id="222")
        service = UserService(db_session)

        result = await service.create_user(data)

        cursor = await db_session.execute(select(User).where(User.id == result["id"]))
        persisted = cursor.scalars().first()
        assert persisted is not None
        assert persisted.api_key == self.ENCRYPTED_KEY
        assert persisted.api_key != result["api_key"]

    @patch("modules.user.services.generate_api_key", return_value=(RAW_KEY, ENCRYPTED_KEY))
    async def test_create_user_without_full_name(self, mock_generate_api_key, db_session: AsyncSession):
        data = CreateUserSchema(telegram_id="333")
        service = UserService(db_session)

        result = await service.create_user(data)

        assert result["full_name"] is None
        assert result["telegram_id"] == "333"
        assert result["api_key"] == self.RAW_KEY

    async def test_create_user_already_exist(self, db_session: AsyncSession, user: User):
        data = CreateUserSchema(full_name=user.full_name, telegram_id=user.telegram_id)
        service = UserService(db_session)

        with pytest.raises(UserAlreadyExistException):
            await service.create_user(data)

    async def test_get_user_by_api_key_returns_user(
        self, db_session: AsyncSession, user_with_api_key: tuple[User, str]
    ):
        user, raw_key = user_with_api_key
        service = UserService(db_session)

        result = await service.get_user_by_api_key(raw_key)

        assert result == {
            "id": user.id,
            "full_name": user.full_name,
            "telegram_id": user.telegram_id,
            "api_key": user.api_key,
        }

    async def test_get_user_by_api_key_raises_when_user_not_found(self, db_session: AsyncSession):
        service = UserService(db_session)

        with pytest.raises(UserNotFound):
            await service.get_user_by_api_key(self.RAW_KEY)
