from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

DataT = TypeVar("DataT")


class BaseSchema(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchemaMixin(BaseSchema):
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class ValidationErrorDetail(BaseSchema):
    loc: str
    msg: str
    type: str


class ApiError(BaseSchema):
    code: str
    message: str
    detail: list[ValidationErrorDetail] | None = None


class ApiResponse(BaseSchema, Generic[DataT]):
    success: bool = True
    data: DataT | None = None
    errors: ApiError | None = None
