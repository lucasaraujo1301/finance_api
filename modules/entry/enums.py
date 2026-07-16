import enum


class EntryTypeEnum(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class PaymentMethodEnum(enum.Enum):
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    CASH = "cash"
