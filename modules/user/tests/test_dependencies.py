from unittest.mock import AsyncMock, patch

import jwt
import pytest

from fastapi.security import HTTPAuthorizationCredentials

from modules.user.dependencies import get_current_user, require_superuser
from modules.user.exceptions import InvalidCredentials, SuperuserRequired
from modules.user.models import UserModel
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserDependencies:
    @patch("modules.user.dependencies.jwt.decode")
    async def test_get_current_user_returns_user(self, decode_mock, user):
        user_service = AsyncMock(spec=UserService)
        user_service.get_by_id.return_value = user
        decode_mock.return_value = {"sub": str(user.id), "type": "access"}

        result = await get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="access-token"),
            user_service,
        )

        assert result is user
        user_service.get_by_id.assert_awaited_once_with(str(user.id))

    @patch("modules.user.dependencies.jwt.decode")
    async def test_get_current_user_rejects_invalid_token(self, decode_mock):
        error = jwt.InvalidTokenError("Invalid token")
        decode_mock.side_effect = error

        with pytest.raises(InvalidCredentials) as exc_info:
            await get_current_user(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token"),
                AsyncMock(spec=UserService),
            )

        assert exc_info.value.__cause__ is error

    @patch("modules.user.dependencies.jwt.decode")
    async def test_get_current_user_rejects_refresh_token(self, decode_mock):
        decode_mock.return_value = {"sub": "user-id", "type": "refresh"}

        with pytest.raises(InvalidCredentials) as exc_info:
            await get_current_user(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="refresh-token"),
                AsyncMock(spec=UserService),
            )

        assert isinstance(exc_info.value.__cause__, jwt.InvalidTokenError)

    async def test_require_superuser_returns_superuser(self, user: UserModel):
        user.is_superuser = True

        assert await require_superuser(user) is user

    async def test_require_superuser_rejects_regular_user(self, user: UserModel):
        user.is_superuser = False

        with pytest.raises(SuperuserRequired):
            await require_superuser(user)
