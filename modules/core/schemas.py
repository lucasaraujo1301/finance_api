from datetime import datetime

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseSchema(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchemaMixin(BaseSchema):
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
