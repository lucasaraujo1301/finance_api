import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.dependencies import get_current_user
from modules.user.exceptions import ApiKeyMissing
from modules.user.models import User
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserDependencies:
    async def test_get_current_user_returns_user(self, db_session: AsyncSession, user_with_api_key: tuple[User, str]):
        user, raw_key = user_with_api_key
        user_service = UserService(db_session)

        result = await get_current_user(api_key=raw_key, user_service=user_service)

        assert result.id == user.id
        assert result.full_name == user.full_name
        assert result.telegram_id == user.telegram_id
        assert result.created_at == user.created_at
        assert result.api_key == user.api_key

    async def test_get_current_user_raises_when_api_key_missing(self, db_session: AsyncSession):
        user_service = UserService(db_session)

        with pytest.raises(ApiKeyMissing):
            await get_current_user(api_key=None, user_service=user_service)
