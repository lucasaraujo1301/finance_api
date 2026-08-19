from datetime import datetime, timedelta, timezone

import jwt
import pytest

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.user.config import user_settings
from modules.user.exceptions import InvalidCredentials, InvalidRefreshToken
from modules.user.models import UserModel
from modules.user.schemas import LoginSchema
from modules.user.services import AuthService, UserService


@pytest.mark.asyncio(loop_scope="session")
class TestAuthService:
    def _get_service(self, db_session: AsyncSession) -> AuthService:
        password_hash = PasswordHash.recommended()
        return AuthService(UserService(logger, db_session, password_hash), password_hash, user_settings)

    async def test_login_returns_tokens_with_valid_claims(self, db_session: AsyncSession):
        password = "secret-password"
        user = UserModel(
            full_name="Alice",
            telegram_id="login-user",
            password=PasswordHash.recommended().hash(password),
            is_superuser=True,
        )
        db_session.add(user)
        await db_session.flush()

        result = await self._get_service(db_session).login(LoginSchema(telegram_id=user.telegram_id, password=password))

        payload = jwt.decode(
            result.access_token,
            user_settings.JWT_SECRET_KEY,
            algorithms=[user_settings.JWT_ALGORITHM],
            issuer=user_settings.JWT_ISSUER,
            audience=user_settings.JWT_AUDIENCE,
        )
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "access"
        assert result.full_name == user.full_name
        assert result.is_superuser is True

    async def test_login_rejects_invalid_credentials(self, db_session: AsyncSession, user_with_password):
        user, _ = user_with_password

        with pytest.raises(InvalidCredentials):
            await self._get_service(db_session).login(
                LoginSchema(telegram_id=user.telegram_id, password="wrong-password")
            )

    async def test_refresh_token_returns_new_token_pair(self, db_session: AsyncSession):
        password = "secret-password"
        user = UserModel(
            full_name="Alice",
            telegram_id="refresh-user",
            password=PasswordHash.recommended().hash(password),
        )
        db_session.add(user)
        await db_session.flush()
        service = self._get_service(db_session)
        login_result = await service.login(LoginSchema(telegram_id=user.telegram_id, password=password))

        result = await service.refresh_token(login_result.refresh_token)

        payload = jwt.decode(
            result.refresh_token,
            user_settings.JWT_SECRET_KEY,
            algorithms=[user_settings.JWT_ALGORITHM],
            issuer=user_settings.JWT_ISSUER,
            audience=user_settings.JWT_AUDIENCE,
        )
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "refresh"

    async def test_refresh_rejects_access_token(self, db_session: AsyncSession):
        password = "secret-password"
        user = UserModel(
            telegram_id="access-token-user",
            password=PasswordHash.recommended().hash(password),
        )
        db_session.add(user)
        await db_session.flush()
        service = self._get_service(db_session)
        login_result = await service.login(LoginSchema(telegram_id=user.telegram_id, password=password))

        with pytest.raises(InvalidRefreshToken):
            await service.refresh_token(login_result.access_token)

    @pytest.mark.parametrize(
        ("claim", "value"),
        [("iss", "unexpected-issuer"), ("aud", "unexpected-audience")],
    )
    async def test_refresh_rejects_unexpected_issuer_or_audience(
        self,
        db_session: AsyncSession,
        user: UserModel,
        claim: str,
        value: str,
    ):
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "type": "refresh",
            "iss": user_settings.JWT_ISSUER,
            "aud": user_settings.JWT_AUDIENCE,
            "iat": now,
            "exp": now + timedelta(minutes=5),
            claim: value,
        }
        token = jwt.encode(payload, user_settings.JWT_SECRET_KEY, algorithm=user_settings.JWT_ALGORITHM)

        with pytest.raises(InvalidRefreshToken):
            await self._get_service(db_session).refresh_token(token)
