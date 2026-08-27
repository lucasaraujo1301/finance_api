from datetime import timedelta

import jwt

from pwdlib import PasswordHash

from modules.user.config import UserSettings
from modules.user.exceptions import InvalidCredentials, InvalidRefreshToken, UserNotFound
from modules.user.models import UserModel
from modules.user.schemas import LoginSchema, TokenSchema, UserSchema
from modules.user.services.user_service import UserService
from modules.user.tokens import create_access_token


class AuthService:
    def __init__(self, user_service: UserService, password_hash: PasswordHash, settings: UserSettings):
        self._user_service = user_service
        self._password_hash = password_hash
        self._settings = settings

    async def login(self, data: LoginSchema) -> TokenSchema:
        try:
            user = await self._user_service.get_by_email(str(data.email))
        except UserNotFound as err:
            raise InvalidCredentials() from err

        if not self._password_hash.verify(data.password, user.password):
            raise InvalidCredentials()

        return self._create_token_response(user)

    async def refresh_token(self, refresh_token: str) -> TokenSchema:
        try:
            payload = jwt.decode(
                refresh_token,
                self._settings.JWT_SECRET_KEY,
                algorithms=[self._settings.JWT_ALGORITHM],
                audience=self._settings.JWT_AUDIENCE,
                issuer=self._settings.JWT_ISSUER,
            )
            if payload.get("type") != "refresh":
                raise InvalidRefreshToken()
            user = await self._user_service.get_by_id(payload["sub"])
        except (jwt.InvalidTokenError, KeyError, UserNotFound) as err:
            raise InvalidRefreshToken() from err

        return self._create_token_response(user)

    def _create_token_response(self, user: UserModel) -> TokenSchema:
        return TokenSchema(
            access_token=create_access_token(user.id, self._settings),
            refresh_token=create_access_token(
                user.id,
                self._settings,
                token_type="refresh",
                expires_delta=timedelta(days=self._settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            ),
            full_name=user.full_name,
            is_superuser=user.is_superuser,
        )

    def create_password_update_url(self, user: UserSchema) -> str:
        token = create_access_token(
            user.id,
            self._settings,
            token_type="password_setup",
            expires_delta=timedelta(minutes=self._settings.JWT_PASSWORD_UPDATE_TOKEN_EXPIRE_MINUTES),
        )
        return f"http://localhost:3000/reset-password?token={token}"

    async def get_user_from_jwt(
        self,
        token: str,
        expected_type: str,
        invalid_token_exception: type[Exception],
    ) -> UserModel:
        try:
            payload = jwt.decode(
                token,
                self._settings.JWT_SECRET_KEY,
                algorithms=[self._settings.JWT_ALGORITHM],
                audience=self._settings.JWT_AUDIENCE,
                issuer=self._settings.JWT_ISSUER,
            )
            if payload.get("type") != expected_type:
                raise jwt.InvalidTokenError(f"{expected_type} token required")
            user = await self._user_service.get_by_id(payload["sub"])
        except (jwt.InvalidTokenError, KeyError, UserNotFound) as err:
            raise invalid_token_exception() from err

        return user
