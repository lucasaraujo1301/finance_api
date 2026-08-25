from uuid import UUID

from pydantic import EmailStr

from modules.core.schemas import BaseSchema, TimestampSchemaMixin


class BaseUserSchema(BaseSchema):
    full_name: str | None = None
    email: EmailStr
    telegram_id: str


class CreateUserSchema(BaseUserSchema):
    password: str
    is_superuser: bool = False


class TelegramUserCreateSchema(BaseUserSchema):
    pass


class LoginSchema(BaseSchema):
    email: EmailStr
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
    needs_password_update: bool


class TelegramUserResponseSchema(UserSchema):
    password_update_url: str


class PatchUserSchema(BaseSchema):
    password: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None


class PasswordUpdateSchema(BaseSchema):
    password: str
