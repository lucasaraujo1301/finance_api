from datetime import date
from uuid import UUID

from fastapi_pagination import Page
from pydantic import BaseModel, Field, field_validator, model_validator

from modules.core.schemas import BaseSchema, TimestampSchemaMixin
from modules.core.types import Balance, Money
from modules.entry.enums import EntryTypeEnum, PaymentMethodEnum
from modules.entry.types import EntryType, PaymentMethod


class BaseEntrySchema(BaseSchema):
    amount: Money
    entry_type: EntryType
    payment_method: PaymentMethod
    category: str
    description: str | None
    payment_date: date


class EntryRequestSchema(BaseEntrySchema):
    entry_type: EntryType = EntryTypeEnum.DEBIT
    payment_date: date = Field(default_factory=date.today)
    category: str = Field(max_length=125)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("payment_date")
    @classmethod
    def validate_payment_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("payment_date cannot be in the future")
        return value


class TelegramEntryRequestSchema(EntryRequestSchema):
    telegram_id: str


class EntrySchema(TimestampSchemaMixin, BaseEntrySchema):
    id: UUID


class EntrySummaryFilterSchema(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self


class EntryFilterSchema(EntrySummaryFilterSchema):
    category: str | None = None
    payment_method: PaymentMethodEnum | None = None
    entry_type: EntryTypeEnum | None = None


class EntrySummarySchema(BaseSchema):
    last_balance: Balance | None = None
    balance: Balance
    current_balance: Balance
    by_payment_method: dict[PaymentMethodEnum, int]
    by_entry_type: dict[EntryTypeEnum, int]


EntryPage = Page[EntrySchema]
