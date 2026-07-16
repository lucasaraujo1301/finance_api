from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from modules.core.models import Base, TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    api_key: Mapped[str] = mapped_column(unique=True, index=True)
