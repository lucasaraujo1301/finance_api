from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.models import User
from modules.user.repository import UserRepository
from modules.user.schemas import CreateUserSchema, UserSchema
from modules.user.utils import generate_api_key


class UserService:
    def __init__(self, db_session: AsyncSession):
        self._repository = UserRepository(db_session)

    async def create_user(self, data: CreateUserSchema) -> dict:
        raw_key, encrypted_key = generate_api_key()
        user = User(full_name=data.full_name, telegram_id=data.telegram_id)
        user.api_key = encrypted_key
        await self._repository.create(user)
        return {
            **UserSchema.model_validate(user).model_dump(),
            "api_key": raw_key,
        }
