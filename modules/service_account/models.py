from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from modules.core.models import Base


class ServiceAccountModel(Base):
    __tablename__ = "service_accounts"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(length=64), unique=True, index=True)
