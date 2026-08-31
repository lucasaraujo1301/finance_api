from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.core.models import Base
from modules.finance.enums import EntryTypeEnum, PaymentMethodEnum
from modules.user.models import UserModel


class EntryModel(Base):
    __tablename__ = "entries"

    entry_type: Mapped[EntryTypeEnum] = mapped_column(
        Enum(EntryTypeEnum, values_callable=EntryTypeEnum.values, name="entrytype")
    )
    payment_method: Mapped[PaymentMethodEnum] = mapped_column(
        Enum(PaymentMethodEnum, values_callable=PaymentMethodEnum.values, name="paymentmethod")
    )
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.now())
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(length=125), nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=255), nullable=True)

    # FK
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_by_service_account_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("service_accounts.id"),
        nullable=True,
    )
    user: Mapped[UserModel] = relationship()
