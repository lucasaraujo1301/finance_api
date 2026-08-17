from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from modules.core.tests.fixtures import BaseFactory
from modules.user.models import UserModel


class UserFactory(BaseFactory[UserModel]):
    __model__ = UserModel

    full_name = Use(SQLAlchemyFactory.__faker__.name)
    telegram_id = Use(lambda: str(SQLAlchemyFactory.__faker__.unique.random_number(digits=4)))
