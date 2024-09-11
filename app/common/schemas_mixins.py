import datetime
import re

from pydantic import BaseModel, field_validator, Field, model_validator
from sqlalchemy.testing import exclude
from typing_extensions import Self


class CreatedAtUpdatedAtMixin(BaseModel):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class PasswordCreationMixin(BaseModel):
    password: str = Field(exclude=True)
    repeat_password: str = Field(exclude=True)

    @field_validator('password')
    @classmethod
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
