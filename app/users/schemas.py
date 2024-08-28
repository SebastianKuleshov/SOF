from pydantic import BaseModel, ConfigDict, EmailStr

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.common.schemas_mixins import PasswordCreationMixin
from app.permissions.schemas import PermissionOutSchema, PermissionNameSchema


class UserBaseSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(PasswordCreationMixin, UserBaseSchema):
    nick_name: str


class UserInRequestSchema(UserBaseSchema):
    nick_name: str
    permissions: set[str]


class UserUpdateSchema(UserBaseSchema):
    nick_name: str | None = None
    email: EmailStr | None = None
    biography: str | None = None


class UserUpdatePayloadSchema(UserUpdateSchema):
    s3_files: list[str] | None = None


class UserOutSchema(UserBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    nick_name: str
    biography: str | None = None
    reputation: int
    avatar_url: str | None = None
