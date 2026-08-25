import pytest

from pwdlib import PasswordHash

from modules.core.logger import logger
from modules.user.config import user_settings
from modules.user.repository import UserRepository
from modules.user.services import AuthService, UserService


@pytest.fixture
def password_hash() -> PasswordHash:
    return PasswordHash.recommended()


@pytest.fixture
def user_service(user_repository: UserRepository, password_hash: PasswordHash) -> UserService:
    return UserService(logger, user_repository, password_hash)


@pytest.fixture
def auth_service(user_service: UserService, password_hash: PasswordHash) -> AuthService:
    return AuthService(user_service, password_hash, user_settings)
