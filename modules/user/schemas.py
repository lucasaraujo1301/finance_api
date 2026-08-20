from uuid import UUID

from modules.core.schemas import BaseSchema, TimestampSchemaMixin


class BaseUserSchema(BaseSchema):
    full_name: str | None = None
    telegram_id: str


class CreateUserSchema(BaseUserSchema):
    password: str
    is_superuser: bool = False


class TelegramUserCreateSchema(BaseUserSchema):
    pass


class LoginSchema(BaseSchema):
    telegram_id: str
    password: str


class RefreshTokenSchema(BaseSchema):
    refresh_token: str


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str
    full_name: str | None
    is_superuser: bool


class UserSchema(TimestampSchemaMixin, BaseUserSchema):
    id: UUID
    is_superuser: bool
