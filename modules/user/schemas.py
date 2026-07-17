from uuid import UUID

from modules.core.schemas import BaseSchema, TimestampSchemaMixin


class CreateUserSchema(BaseSchema):
    full_name: str | None = None
    telegram_id: str


class BaseUserSchema(BaseSchema):
    id: UUID
    full_name: str | None = None
    telegram_id: str


class UserSchema(TimestampSchemaMixin, BaseUserSchema):
    api_key: str
