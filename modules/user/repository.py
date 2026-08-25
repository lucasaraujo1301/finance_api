from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.user.models import UserModel


class UserRepository(BaseRepository[UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)

    async def get_user_by_telegram_id(self, telegram_id: str) -> UserModel | None:
        result = await self._session.execute(select(UserModel).where(UserModel.telegram_id == telegram_id))
        return result.scalars().first()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        result = await self._session.execute(select(UserModel).where(UserModel.email == email))
        return result.scalars().first()
