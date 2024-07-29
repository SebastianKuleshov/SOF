from pydantic import BaseModel, ConfigDict

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin


class TagBaseSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class TagUpdateSchema(TagBaseSchema):
    name: str | None = None


class TagOutSchema(CreatedAtUpdatedAtMixin, TagBaseSchema):
    id: int
