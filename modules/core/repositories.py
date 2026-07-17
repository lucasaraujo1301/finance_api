from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model_class: type[T]):
        self._session = session
        self._model_class = model_class

    async def create(self, instance: T) -> T:
        self._session.add(instance)
        await self._session.commit()
        await self._session.refresh(instance)
        return instance

    async def get_by_id(self, model_id: UUID | str) -> T | None:
        return await self._session.get(self._model_class, model_id)

    async def update(self, model: T) -> T:
        model.updated_at = datetime.now(timezone.utc)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return model

    async def delete(self, model: T) -> None:
        model.deleted_at = datetime.now(timezone.utc)
        await self.update(model)
