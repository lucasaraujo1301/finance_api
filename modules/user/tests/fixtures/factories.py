from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from modules.user.models import User
from modules.user.utils import generate_api_key


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User

    full_name = Use(SQLAlchemyFactory.__faker__.name)
    telegram_id = Use(lambda: str(SQLAlchemyFactory.__faker__.unique.random_number(digits=4)))
    api_key = Use(lambda: generate_api_key()[1])

    @classmethod
    def api_key_pair(cls) -> tuple[str, str]:
        return generate_api_key()
