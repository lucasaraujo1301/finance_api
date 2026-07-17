from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from modules.core.tests.fixtures import BaseFactory
from modules.user.models import UserModel
from modules.user.utils import generate_api_key


class UserFactory(BaseFactory[UserModel]):
    __model__ = UserModel

    full_name = Use(SQLAlchemyFactory.__faker__.name)
    telegram_id = Use(lambda: str(SQLAlchemyFactory.__faker__.unique.random_number(digits=4)))
    api_key = Use(lambda: generate_api_key()[1])

    @classmethod
    def api_key_pair(cls) -> tuple[str, str]:
        return generate_api_key()
