import re

from pydantic import BaseModel, ConfigDict, field_validator, EmailStr, \
    model_validator, Field
from typing_extensions import Self

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin


class UserBaseSchema(BaseModel):
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserCreateSchema(UserBaseSchema):
    nick_name: str
    password: str
    repeat_password: str = Field(exclude=True)

    @classmethod
    @field_validator('password')
    def password_validator(cls, value: str) -> str:
        len_regex = re.compile(r"\S{8,}")
        if not re.fullmatch(len_regex, value):
            raise ValueError(
                "Password must be at least 8 characters long."
            )
        lower_regex = re.compile(r"[a-z]+")
        if not re.search(lower_regex, value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )
        upper_regex = re.compile(r"[A-Z]+")
        if not re.search(upper_regex, value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )
        digit_regex = re.compile(r"\d+")
        if not re.search(digit_regex, value):
            raise ValueError(
                "Password must contain at least one digit."
            )
        special_regex = re.compile(r"[^a-zA-z0-9\s:\"]")
        if not re.search(special_regex, value):
            raise ValueError(
                "Password must contain at least one special character."
            )
        return value

    @model_validator(mode='after')
    def repeat_password_validator(self) -> Self:
        if self.password != self.repeat_password:
            raise ValueError(
                "Passwords do not match."
            )
        return self


class UserLoginSchema(BaseModel):
    password: str


class UserUpdateSchema(UserBaseSchema):
    nick_name: str | None = None
    email: EmailStr | None = None
    biography: str | None = None


class UserOutSchema(UserBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    nick_name: str
