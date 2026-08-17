from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import UserModel
from modules.user.repository import UserRepository
from modules.user.schemas import CreateUserSchema, UserSchema


class UserService:
    def __init__(self, logger: Logger, db_session: AsyncSession):
        self.logger = logger
        self._repository = UserRepository(db_session)

    async def create_user(self, data: CreateUserSchema) -> UserSchema:
        self.logger.info("Creating user")
        if await self._repository.get_user_by_telegram_id(data.telegram_id):
            raise UserAlreadyExistException()

        user = UserModel(full_name=data.full_name, telegram_id=data.telegram_id)

        self.logger.info("Saving user at database.")
        await self._repository.create(user)
        return UserSchema.model_validate(user)

    async def get_by_telegram_id(self, telegram_id: str) -> UserModel:
        user = await self._repository.get_user_by_telegram_id(telegram_id)
        if user is None:
            raise UserNotFound()

        return user
