from datetime import datetime, timedelta, timezone
from logging import Logger
from secrets import token_urlsafe

import jwt

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.config import UserSettings
from modules.user.exceptions import (
    InvalidCredentials,
    InvalidRefreshToken,
    UserAlreadyExistException,
    UserNotFound,
)
from modules.user.models import UserModel
from modules.user.repository import UserRepository
from modules.user.schemas import (
    CreateUserSchema,
    LoginSchema,
    PatchUserSchema,
    TelegramUserCreateSchema,
    TokenSchema,
    UserSchema,
)
from modules.user.tokens import create_access_token


class UserService:
    def __init__(self, logger: Logger, db_session: AsyncSession, password_hash: PasswordHash):
        self.logger = logger
        self._repository = UserRepository(db_session)
        self._password_hash = password_hash

    async def create_user(self, data: CreateUserSchema) -> UserSchema:
        self.logger.info("Creating user")
        if await self._repository.get_user_by_telegram_id(data.telegram_id):
            raise UserAlreadyExistException()

        user = UserModel(
            full_name=data.full_name,
            telegram_id=data.telegram_id,
            password=self._password_hash.hash(data.password),
            is_superuser=data.is_superuser,
        )

        self.logger.info("Saving user at database.")
        await self._repository.create(user)
        return UserSchema.model_validate(user)

    async def create_telegram_user(self, data: TelegramUserCreateSchema) -> UserSchema:
        return await self.create_user(
            CreateUserSchema(
                full_name=data.full_name,
                telegram_id=data.telegram_id,
                password=token_urlsafe(32),
            )
        )

    async def get_by_telegram_id(self, telegram_id: str) -> UserModel:
        user = await self._repository.get_user_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFound()

        return user

    async def get_by_id(self, user_id: str) -> UserModel:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        return user

    async def update_user(self, user: UserModel, data: PatchUserSchema) -> UserModel:
        if data.full_name:
            user.full_name = data.full_name

        if data.password:
            user.password = self._password_hash.hash(data.password)

        return await self._repository.update(user)


class AuthService:
    def __init__(self, user_service: UserService, password_hash: PasswordHash, settings: UserSettings):
        self._user_service = user_service
        self._password_hash = password_hash
        self._settings = settings

    async def login(self, data: LoginSchema) -> TokenSchema:
        try:
            user = await self._user_service.get_by_telegram_id(data.telegram_id)
        except UserNotFound:
            raise InvalidCredentials() from None

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
        except jwt.InvalidTokenError, KeyError, UserNotFound:
            raise InvalidRefreshToken() from None

        return self._create_token_response(user)

    def _create_token_response(self, user: UserModel) -> TokenSchema:
        return TokenSchema(
            access_token=create_access_token(user, self._settings),
            refresh_token=self._create_token(
                user,
                "refresh",
                timedelta(days=self._settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            ),
            full_name=user.full_name,
            is_superuser=user.is_superuser,
        )

    def _create_token(self, user: UserModel, token_type: str, expires_delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        return jwt.encode(
            {
                "sub": str(user.id),
                "type": token_type,
                "iss": self._settings.JWT_ISSUER,
                "aud": self._settings.JWT_AUDIENCE,
                "iat": now,
                "exp": now + expires_delta,
            },
            self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
        )
