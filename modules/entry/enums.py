import enum

from modules.core.i18n import _


class EntryTypeEnum(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"

    @property
    def label(self) -> str:
        return {
            self.DEBIT: _("Debit"),
            self.CREDIT: _("Credit"),
        }[self]


class PaymentMethodEnum(enum.Enum):
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    CASH = "cash"
    ACCOUNT_TRANSFER = "account_transfer"

    @property
    def label(self) -> str:
        return {
            self.DEBIT_CARD: _("Debit Card"),
            self.CREDIT_CARD: _("Credit Card"),
            self.PIX: _("Pix"),
            self.CASH: _("Cash"),
            self.ACCOUNT_TRANSFER: _("Account Transfer"),
        }[self]
