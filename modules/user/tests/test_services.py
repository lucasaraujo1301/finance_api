import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from modules.user.exceptions import UserAlreadyExistException, UserNotFound
from modules.user.models import UserModel
from modules.user.schemas import CreateUserSchema, PatchUserSchema, TelegramUserCreateSchema


@pytest.mark.asyncio(loop_scope="session")
class TestUserService:
    async def test_create_user_persists_and_returns_user(self, db_session: AsyncSession, user_service, password_hash):
        data = CreateUserSchema(
            full_name="Alice",
            email="alice@example.com",
            telegram_id="111",
            password="secret-password",
        )
        result = await user_service.create_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert result.full_name == "Alice"
        assert result.telegram_id == "111"
        assert persisted.password != data.password
        assert password_hash.verify(data.password, persisted.password)

    async def test_create_user_without_full_name(self, db_session: AsyncSession, user_service):
        data = CreateUserSchema(email="three@example.com", telegram_id="333", password="secret-password")
        result = await user_service.create_user(data)

        assert result.full_name is None
        assert result.telegram_id == "333"

    async def test_create_superuser(self, db_session: AsyncSession, user_service):
        data = CreateUserSchema(
            email="superuser@example.com",
            telegram_id="superuser",
            password="secret-password",
            is_superuser=True,
        )
        result = await user_service.create_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert persisted.is_superuser is True

    async def test_create_user_already_exist(self, db_session: AsyncSession, user: UserModel, user_service):
        data = CreateUserSchema(
            full_name=user.full_name,
            email=user.email,
            telegram_id=user.telegram_id,
            password="secret-password",
        )
        with pytest.raises(UserAlreadyExistException, match=UserAlreadyExistException().message):
            await user_service.create_user(data)

    async def test_create_telegram_user_generates_hashed_password(self, db_session: AsyncSession, user_service):
        data = TelegramUserCreateSchema(full_name="Telegram User", email="telegram@example.com", telegram_id="444")
        result = await user_service.create_telegram_user(data)

        persisted = await db_session.get(UserModel, result.id)
        assert persisted is not None
        assert persisted.password.startswith("$argon2")
        assert persisted.email == data.email
        assert persisted.needs_password_update is True
        assert "password" not in result.model_dump()

    async def test_get_by_telegram_id_returns_user(self, db_session: AsyncSession, user: UserModel, user_service):
        result = await user_service.get_by_telegram_id(user.telegram_id)

        assert result.id == user.id
        assert result.full_name == user.full_name
        assert result.telegram_id == user.telegram_id
        assert result.created_at == user.created_at

    async def test_get_by_telegram_id_raises_when_user_not_found(self, db_session: AsyncSession, user_service):
        with pytest.raises(UserNotFound, match=UserNotFound().message):
            await user_service.get_by_telegram_id("missing")

    async def test_update_user_persists_full_name(self, db_session: AsyncSession, user: UserModel, user_service):
        result = await user_service.update_user(user, PatchUserSchema(full_name="Updated Name"))

        persisted = await db_session.get(UserModel, user.id)
        assert result.full_name == "Updated Name"
        assert persisted is not None
        assert persisted.full_name == "Updated Name"

    async def test_update_user_hashes_password_and_preserves_omitted_name(
        self,
        db_session: AsyncSession,
        user: UserModel,
        user_service,
        password_hash,
    ):
        original_name = user.full_name

        result = await user_service.update_user(user, PatchUserSchema(password="new-secret-password"))

        assert result.full_name == original_name
        assert result.password != "new-secret-password"
        assert password_hash.verify("new-secret-password", result.password)
