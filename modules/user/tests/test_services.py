import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import UserModel
from modules.user.schemas import CreateUserSchema
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserService:
    async def test_create_user_persists_and_returns_user(self, db_session: AsyncSession):
        data = CreateUserSchema(full_name="Alice", telegram_id="111")
        service = UserService(logger, db_session)

        result = await service.create_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert result.full_name == "Alice"
        assert result.telegram_id == "111"

    async def test_create_user_without_full_name(self, db_session: AsyncSession):
        data = CreateUserSchema(telegram_id="333")
        service = UserService(logger, db_session)

        result = await service.create_user(data)

        assert result.full_name is None
        assert result.telegram_id == "333"

    async def test_create_user_already_exist(self, db_session: AsyncSession, user: UserModel):
        data = CreateUserSchema(full_name=user.full_name, telegram_id=user.telegram_id)
        service = UserService(logger, db_session)

        with pytest.raises(UserAlreadyExistException, match=UserAlreadyExistException().message):
            await service.create_user(data)

    async def test_get_by_telegram_id_returns_user(self, db_session: AsyncSession, user: UserModel):
        service = UserService(logger, db_session)

        result = await service.get_by_telegram_id(user.telegram_id)

        assert result.id == user.id
        assert result.full_name == user.full_name
        assert result.telegram_id == user.telegram_id
        assert result.created_at == user.created_at

    async def test_get_by_telegram_id_raises_when_user_not_found(self, db_session: AsyncSession):
        service = UserService(logger, db_session)

        with pytest.raises(UserNotFound, match=UserNotFound().message):
            await service.get_by_telegram_id("missing")
