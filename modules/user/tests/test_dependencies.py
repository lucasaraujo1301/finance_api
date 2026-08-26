from unittest.mock import AsyncMock

import pytest

from fastapi.security import HTTPAuthorizationCredentials

from modules.user.dependencies import get_current_user, get_current_user_from_password_setup, require_superuser
from modules.user.exceptions import InvalidCredentials, InvalidPasswordUpdateToken, SuperuserRequired
from modules.user.models import UserModel
from modules.user.services import AuthService


@pytest.mark.asyncio(loop_scope="session")
class TestUserDependencies:
    async def test_get_current_user_returns_user(self, user):
        auth_service = AsyncMock(spec=AuthService)
        auth_service.get_user_from_jwt.return_value = user

        result = await get_current_user(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="access-token"),
            auth_service,
        )

        assert result is user
        auth_service.get_user_from_jwt.assert_awaited_once_with(
            "access-token",
            "access",
            InvalidCredentials,
        )

    async def test_get_current_user_rejects_missing_token(self):
        with pytest.raises(InvalidCredentials) as exc_info:
            await get_current_user(None, AsyncMock(spec=AuthService))

        assert exc_info.value.__cause__ is None

    async def test_get_current_user_rejects_invalid_token(self):
        auth_service = AsyncMock(spec=AuthService)
        error = InvalidCredentials()
        auth_service.get_user_from_jwt.side_effect = error

        with pytest.raises(InvalidCredentials) as exc_info:
            await get_current_user(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="refresh-token"),
                auth_service,
            )

        assert exc_info.value is error

    async def test_require_superuser_returns_superuser(self, user: UserModel):
        user.is_superuser = True

        assert await require_superuser(user) is user

    async def test_require_superuser_rejects_regular_user(self, user: UserModel):
        user.is_superuser = False

        with pytest.raises(SuperuserRequired):
            await require_superuser(user)

    async def test_get_current_user_from_password_setup_returns_user_with_pending_update(self, user: UserModel):
        user.needs_password_update = True
        auth_service = AsyncMock(spec=AuthService)
        auth_service.get_user_from_jwt.return_value = user

        result = await get_current_user_from_password_setup(
            HTTPAuthorizationCredentials(scheme="Bearer", credentials="setup-token"),
            auth_service,
        )

        assert result is user
        auth_service.get_user_from_jwt.assert_awaited_once_with(
            "setup-token",
            "password_setup",
            InvalidPasswordUpdateToken,
        )

    async def test_get_current_user_from_password_setup_rejects_missing_token(self):
        with pytest.raises(InvalidPasswordUpdateToken):
            await get_current_user_from_password_setup(None, AsyncMock(spec=AuthService))

    async def test_get_current_user_from_password_setup_rejects_user_without_pending_update(self, user: UserModel):
        user.needs_password_update = False
        auth_service = AsyncMock(spec=AuthService)
        auth_service.get_user_from_jwt.return_value = user

        with pytest.raises(InvalidPasswordUpdateToken):
            await get_current_user_from_password_setup(
                HTTPAuthorizationCredentials(scheme="Bearer", credentials="setup-token"),
                auth_service,
            )
