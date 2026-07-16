from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator

from modules.core.schemas import BaseSchema
from modules.core.types import Money
from modules.entry.enums import EntryTypeEnum
from modules.entry.types import EntryType, PaymentMethod


class BaseEntrySchema(BaseSchema):
    amount: Money
    entry_type: EntryType
    payment_method: PaymentMethod
    category: str
    description: str
    payment_date: date
    is_fixed: bool


class EntryRequestSchema(BaseEntrySchema):
    entry_type: EntryType = EntryTypeEnum.DEBIT
    payment_date: date = Field(default_factory=date.today)
    is_fixed: bool = False
    category: str = Field(max_length=125)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("payment_date cannot be in the future")
        return value


class EntryResponseSchema(BaseEntrySchema):
    id: UUID
    created_at: datetime
