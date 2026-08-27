from logging import Logger
from secrets import token_urlsafe
from uuid import UUID

from pwdlib import PasswordHash

from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import UserModel
from modules.user.repository import UserRepository
from modules.user.schemas import (
    CreateUserSchema,
    PasswordUpdateSchema,
    PatchUserSchema,
    TelegramUserCreateSchema,
    UserSchema,
)


class UserService:
    def __init__(self, logger: Logger, repository: UserRepository, password_hash: PasswordHash):
        self.logger = logger
        self._repository = repository
        self._password_hash = password_hash

    async def create_user(self, data: CreateUserSchema, needs_password_update: bool = False) -> UserSchema:
        self.logger.info("Creating user")
        if await self._repository.get_user_by_telegram_id(data.telegram_id) or await self._repository.get_user_by_email(
            str(data.email)
        ):
            raise UserAlreadyExistException()

        user = UserModel(
            full_name=data.full_name,
            email=str(data.email),
            telegram_id=data.telegram_id,
            password=self._password_hash.hash(data.password),
            is_superuser=data.is_superuser,
            needs_password_update=needs_password_update,
        )

        self.logger.info("Saving user at database.")
        await self._repository.create(user)
        return UserSchema.model_validate(user)

    async def create_telegram_user(self, data: TelegramUserCreateSchema) -> UserSchema:
        return await self.create_user(
            CreateUserSchema(
                full_name=data.full_name,
                email=data.email,
                telegram_id=data.telegram_id,
                password=token_urlsafe(32),
            ),
            needs_password_update=True,
        )

    async def get_by_telegram_id(self, telegram_id: str) -> UserModel:
        user = await self._repository.get_user_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFound()

        return user

    async def get_by_email(self, email: str) -> UserModel:
        user = await self._repository.get_user_by_email(email)
        if user is None:
            raise UserNotFound()

        return user

    async def get_by_id(self, user_id: UUID) -> UserModel:
        user = await self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFound()

        return user

    async def update_user(self, user: UserModel, data: PatchUserSchema) -> UserModel:
        if data.full_name:
            user.full_name = data.full_name

        if data.email:
            user.email = str(data.email)

        if data.password:
            user.password = self._password_hash.hash(data.password)

        return await self._repository.update(user)

    async def update_password(self, user: UserModel, data: PasswordUpdateSchema) -> UserModel:
        user.password = self._password_hash.hash(data.password)
        user.needs_password_update = False
        return await self._repository.update(user)
