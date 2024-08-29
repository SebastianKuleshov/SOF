from pydantic import BaseModel, Field, ConfigDict


class PermissionBaseSchema(BaseModel):
    name: str
    attach_to_superuser: bool = Field(True, exclude=True)

    model_config = ConfigDict(from_attributes=True)


class PermissionOutSchema(PermissionBaseSchema):
    id: int

class PermissionNameSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)

