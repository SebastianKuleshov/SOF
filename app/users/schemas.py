from pydantic import BaseModel, ConfigDict, EmailStr

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin, \
    PasswordCreationMixin


class UserBaseSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(PasswordCreationMixin, UserBaseSchema):
    nick_name: str


class UserCreatePayloadSchema(UserCreateSchema):
    id: str


class UserInRequestSchema(UserBaseSchema):
    nick_name: str
    permissions: set[str]


class UserUpdateSchema(UserBaseSchema):
    biography: str | None = None


class UserUpdatePayloadSchema(UserUpdateSchema):
    avatar_file_storage_id: int | None = None


class UserOutSchema(UserBaseSchema, CreatedAtUpdatedAtMixin):
    id: str
    nick_name: str
    biography: str | None = None
    reputation: int
    avatar_url: str | None = None
