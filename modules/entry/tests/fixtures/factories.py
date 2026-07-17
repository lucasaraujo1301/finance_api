import datetime

from decimal import Decimal

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Use

from modules.core.tests.fixtures import BaseFactory
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.models import EntryModel


class EntryFactory(BaseFactory[EntryModel]):
    __model__ = EntryModel

    entry_type = EntryTypeEnum.DEBIT
    amount = Use(lambda: Decimal("10.50"))
    payment_method = PaymentMethodEnum.CREDIT_CARD
    category = Use(SQLAlchemyFactory.__faker__.word)
    description = Use(SQLAlchemyFactory.__faker__.sentence)
    payment_date = Use(lambda: datetime.date.today())
    is_fixed = False
