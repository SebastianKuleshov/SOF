from typing import Text

from pydantic import BaseModel, Field, ConfigDict

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.questions.schemas import QuestionOutSchema
from app.users.schemas import UserOutSchema


class AnswerBaseSchema(BaseModel):
    body: Text = Field(min_length=30, max_length=3500)

    model_config = ConfigDict(from_attributes=True)


class AnswerCreateSchema(AnswerBaseSchema):
    question_id: int


class AnswerCreatePayloadSchema(AnswerCreateSchema):
    user_id: int


class AnswerUpdateSchema(AnswerBaseSchema):
    body: Text = Field(None, min_length=30, max_length=3500)


class AnswerOutSchema(AnswerBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    user_id: int
    question_id: int


class AnswerWithUserSchema(AnswerOutSchema):
    user: UserOutSchema


class AnswerWithJoinsOutSchema(AnswerOutSchema):
    user: UserOutSchema
    question: QuestionOutSchema
