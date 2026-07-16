from datetime import date
from decimal import Decimal

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from modules.core.models import Base, TimestampMixin
from modules.entry.enums import EntryType, PaymentMethod
from modules.user.models import User


class Entry(TimestampMixin, Base):
    __tablename__ = "entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entry_type: Mapped[EntryType]
    payment_method: Mapped[PaymentMethod]
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.now())
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    category: Mapped[str] = mapped_column(String(length=125), nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)

    # FK
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped[User] = relationship()
