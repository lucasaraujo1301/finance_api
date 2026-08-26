from datetime import datetime, timedelta, timezone

import jwt
import pytest

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.config import user_settings
from modules.user.exceptions import InvalidCredentials, InvalidPasswordUpdateToken, InvalidRefreshToken
from modules.user.models import UserModel
from modules.user.schemas import LoginSchema


@pytest.mark.asyncio(loop_scope="session")
class TestAuthService:
    async def test_login_returns_tokens_with_valid_claims(self, db_session: AsyncSession, auth_service):
        password = "secret-password"
        user = UserModel(
            full_name="Alice",
            email="alice@example.com",
            telegram_id="login-user",
            password=PasswordHash.recommended().hash(password),
            is_superuser=True,
        )
        db_session.add(user)
        await db_session.flush()

        result = await auth_service.login(LoginSchema(email=user.email, password=password))

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

    async def test_login_rejects_invalid_credentials(self, db_session: AsyncSession, user_with_password, auth_service):
        user, _ = user_with_password

        with pytest.raises(InvalidCredentials):
            await auth_service.login(LoginSchema(email=user.email, password="wrong-password"))

    async def test_login_rejects_unknown_email(self, db_session: AsyncSession, auth_service):
        with pytest.raises(InvalidCredentials):
            await auth_service.login(LoginSchema(email="missing@example.com", password="secret-password"))

    async def test_refresh_token_returns_new_token_pair(self, db_session: AsyncSession, auth_service):
        password = "secret-password"
        user = UserModel(
            full_name="Alice",
            telegram_id="refresh-user",
            email="refresh@example.com",
            password=PasswordHash.recommended().hash(password),
        )
        db_session.add(user)
        await db_session.flush()
        login_result = await auth_service.login(LoginSchema(email=user.email, password=password))

        result = await auth_service.refresh_token(login_result.refresh_token)

        payload = jwt.decode(
            result.refresh_token,
            user_settings.JWT_SECRET_KEY,
            algorithms=[user_settings.JWT_ALGORITHM],
            issuer=user_settings.JWT_ISSUER,
            audience=user_settings.JWT_AUDIENCE,
        )
        assert payload["sub"] == str(user.id)
        assert payload["type"] == "refresh"

    async def test_refresh_rejects_access_token(self, db_session: AsyncSession, auth_service):
        password = "secret-password"
        user = UserModel(
            telegram_id="access-token-user",
            email="access@example.com",
            password=PasswordHash.recommended().hash(password),
        )
        db_session.add(user)
        await db_session.flush()
        login_result = await auth_service.login(LoginSchema(email=user.email, password=password))

        with pytest.raises(InvalidRefreshToken):
            await auth_service.refresh_token(login_result.access_token)

    async def test_refresh_rejects_malformed_token(self, auth_service):
        with pytest.raises(InvalidRefreshToken):
            await auth_service.refresh_token("not-a-jwt")

    async def test_refresh_rejects_token_without_subject(self, auth_service):
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "type": "refresh",
                "iss": user_settings.JWT_ISSUER,
                "aud": user_settings.JWT_AUDIENCE,
                "iat": now,
                "exp": now + timedelta(minutes=5),
            },
            user_settings.JWT_SECRET_KEY,
            algorithm=user_settings.JWT_ALGORITHM,
        )

        with pytest.raises(InvalidRefreshToken):
            await auth_service.refresh_token(token)

    async def test_get_user_from_jwt_rejects_wrong_token_type(self, db_session: AsyncSession, user, auth_service):
        token = auth_service.create_password_update_url(user).split("token=", 1)[1]

        with pytest.raises(InvalidCredentials):
            await auth_service.get_user_from_jwt(token, "access", InvalidCredentials)

    async def test_password_setup_token_resolves_only_before_password_update(
        self,
        db_session: AsyncSession,
        auth_service,
    ):
        password = "temporary-password"
        user = UserModel(
            email="setup@example.com",
            telegram_id="setup-user",
            password=PasswordHash.recommended().hash(password),
            needs_password_update=True,
        )
        db_session.add(user)
        await db_session.flush()

        setup_token = auth_service.create_password_update_url(user).split("token=", 1)[1]
        resolved_user = await auth_service.get_user_from_jwt(
            setup_token,
            "password_setup",
            InvalidPasswordUpdateToken,
        )

        assert resolved_user.id == user.id

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
        auth_service,
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
            await auth_service.refresh_token(token)
