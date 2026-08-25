from sqlalchemy import Boolean, String, false
from sqlalchemy.orm import Mapped, mapped_column

from modules.core.models import Base


class UserModel(Base):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(length=255), nullable=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, index=True, nullable=False)
    telegram_id: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column(String(length=255))
    is_superuser: Mapped[bool] = mapped_column(default=False)
    needs_password_update: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), nullable=False)
