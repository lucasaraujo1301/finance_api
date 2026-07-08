from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_user_by_api_key(self, api_key: str) -> User | None:
        result = await self._session.execute(select(User).where(User.api_key == api_key))
        return result.scalars().first()

    async def get_user_by_telegram_id(self, telegram_id: str) -> User | None:
        result = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()
