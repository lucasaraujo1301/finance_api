from uuid import UUID

from modules.core.schemas import BaseSchema


class CreateUserSchema(BaseSchema):
    full_name: str | None = None
    telegram_id: str


class UserSchema(BaseSchema):
    id: UUID
    full_name: str | None = None
    telegram_id: str
    api_key: str
