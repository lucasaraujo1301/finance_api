from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from modules.core.tests.fixtures import BaseFactory
from modules.service_account.models import ServiceAccountModel
from modules.service_account.utils import generate_api_key


class ServiceAccountFactory(BaseFactory[ServiceAccountModel]):
    __model__ = ServiceAccountModel

    name = Use(lambda: SQLAlchemyFactory.__faker__.unique.user_name())
    api_key = Use(lambda: generate_api_key()[1])

    @classmethod
    def api_key_pair(cls) -> tuple[str, str]:
        return generate_api_key()
