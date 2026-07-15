import enum


class EntryType(enum.Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class PaymentMethod(enum.Enum):
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    PIX = "pix"
    CASH = "cash"
