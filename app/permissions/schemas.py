from pydantic import BaseModel, Field


class PermissionBaseSchema(BaseModel):
    name: str
    attach_to_superuser: bool = Field(True, exclude=True)

class PermissionOutSchema(PermissionBaseSchema):
    id: int
