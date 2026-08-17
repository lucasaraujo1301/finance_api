from uuid import UUID

from pydantic import Field

from modules.core.schemas import BaseSchema, TimestampSchemaMixin


class CreateServiceAccountSchema(BaseSchema):
    name: str = Field(min_length=1, max_length=255)


class ServiceAccountSchema(TimestampSchemaMixin):
    id: UUID
    name: str


class CreatedServiceAccountSchema(ServiceAccountSchema):
    api_key: str
