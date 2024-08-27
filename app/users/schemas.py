from pydantic import BaseModel, ConfigDict, EmailStr

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.common.schemas_mixins import PasswordCreationMixin


class UserBaseSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(PasswordCreationMixin, UserBaseSchema):
    nick_name: str


class UserCreatePayloadSchema(UserCreateSchema):
    id: str

class UserLoginSchema(BaseModel):
    password: str


class UserUpdateSchema(UserBaseSchema):
    nick_name: str | None = None
    email: EmailStr | None = None
    biography: str | None = None


class UserUpdatePayloadSchema(UserUpdateSchema):
    s3_files: list[str] | None = None


class UserOutSchema(UserBaseSchema, CreatedAtUpdatedAtMixin):
    id: str
    nick_name: str
    biography: str | None = None
    reputation: int
    avatar_url: str | None = None
