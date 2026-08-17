from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.repositories import BaseRepository
from modules.service_account.models import ServiceAccountModel


class ServiceAccountRepository(BaseRepository[ServiceAccountModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ServiceAccountModel)

    async def get_by_name(self, name: str) -> ServiceAccountModel | None:
        result = await self._session.execute(select(ServiceAccountModel).where(ServiceAccountModel.name == name))
        return result.scalars().first()

    async def get_by_api_key(self, api_key: str) -> ServiceAccountModel | None:
        result = await self._session.execute(
            select(ServiceAccountModel).where(
                ServiceAccountModel.api_key == api_key,
                ServiceAccountModel.deleted_at.is_(None),
            )
        )
        return result.scalars().first()
