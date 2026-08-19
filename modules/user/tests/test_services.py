import pytest

from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from modules.core.logger import logger
from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import UserModel
from modules.user.schemas import CreateUserSchema, TelegramUserCreateSchema
from modules.user.services import UserService


@pytest.mark.asyncio(loop_scope="session")
class TestUserService:
    def _get_service(
        self,
        db_session: AsyncSession,
        password_hash: PasswordHash | None = None,
    ) -> UserService:
        return UserService(logger, db_session, password_hash or PasswordHash.recommended())

    async def test_create_user_persists_and_returns_user(self, db_session: AsyncSession):
        data = CreateUserSchema(full_name="Alice", telegram_id="111", password="secret-password")
        password_hash = PasswordHash.recommended()
        service = self._get_service(db_session, password_hash)

        result = await service.create_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert result.full_name == "Alice"
        assert result.telegram_id == "111"
        assert persisted.password != data.password
        assert password_hash.verify(data.password, persisted.password)

    async def test_create_user_without_full_name(self, db_session: AsyncSession):
        data = CreateUserSchema(telegram_id="333", password="secret-password")
        service = self._get_service(db_session)

        result = await service.create_user(data)

        assert result.full_name is None
        assert result.telegram_id == "333"

    async def test_create_superuser(self, db_session: AsyncSession):
        data = CreateUserSchema(telegram_id="superuser", password="secret-password", is_superuser=True)
        service = self._get_service(db_session)

        result = await service.create_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert persisted.is_superuser is True

    async def test_create_user_already_exist(self, db_session: AsyncSession, user: UserModel):
        data = CreateUserSchema(full_name=user.full_name, telegram_id=user.telegram_id, password="secret-password")
        service = self._get_service(db_session)

        with pytest.raises(UserAlreadyExistException, match=UserAlreadyExistException().message):
            await service.create_user(data)

    async def test_create_telegram_user_generates_hashed_password(self, db_session: AsyncSession):
        data = TelegramUserCreateSchema(full_name="Telegram User", telegram_id="444")
        service = self._get_service(db_session)

        result = await service.create_telegram_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert persisted.password.startswith("$argon2")
        assert "password" not in result.model_dump()

    async def test_get_by_telegram_id_returns_user(self, db_session: AsyncSession, user: UserModel):
        service = self._get_service(db_session)

        result = await service.get_by_telegram_id(user.telegram_id)

        assert result.id == user.id
        assert result.full_name == user.full_name
        assert result.telegram_id == user.telegram_id
        assert result.created_at == user.created_at

    async def test_get_by_telegram_id_raises_when_user_not_found(self, db_session: AsyncSession):
        service = self._get_service(db_session)

        with pytest.raises(UserNotFound, match=UserNotFound().message):
            await service.get_by_telegram_id("missing")
