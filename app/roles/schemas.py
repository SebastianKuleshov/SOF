from pydantic import BaseModel, ConfigDict

from app.permissions.schemas import PermissionOutSchema


class RoleBaseSchema(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class RoleOutSchema(RoleBaseSchema):
    id: int


class RoleInRequestSchema(RoleBaseSchema):
    id: int
    permissions: list[PermissionOutSchema]
