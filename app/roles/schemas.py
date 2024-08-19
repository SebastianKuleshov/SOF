from pydantic import BaseModel


class RoleBaseSchema(BaseModel):
    name: str

class RoleOutSchema(RoleBaseSchema):
    id: int