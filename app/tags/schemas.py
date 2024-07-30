import datetime

from pydantic import BaseModel, ConfigDict


class TagBaseSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagUpdateSchema(TagBaseSchema):
    name: str | None = None


class TagOutSchema(TagBaseSchema):
    id: int
    created_at: datetime.datetime
