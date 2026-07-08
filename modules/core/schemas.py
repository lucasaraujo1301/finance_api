from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict


class BaseSchema(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
