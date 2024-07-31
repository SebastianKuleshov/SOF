from typing import Text

from pydantic import BaseModel, ConfigDict, Field

from app.answers.schemas import AnswerWithCommentsOutSchema
from app.comments.schemas import CommentOutSchema
from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.users.schemas import UserOutSchema


class QuestionBaseSchema(BaseModel):
    title: str = Field(min_length=10, max_length=150)
    body: Text = Field(min_length=30, max_length=3500)

    model_config = ConfigDict(from_attributes=True)


class QuestionCreateSchema(QuestionBaseSchema):
    user_id: int


class QuestionUpdateSchema(QuestionBaseSchema):
    title: str = Field(None, min_length=10, max_length=150)
    body: Text = Field(None, min_length=30, max_length=3500)
    accepted_answer_id: int | None = None


class QuestionOutSchema(QuestionBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    user_id: int
    accepted_answer_id: int | None


class TagOutSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class QuestionWithTagsOutSchema(QuestionOutSchema):
    tags: list[TagOutSchema]


class QuestionForListOutSchema(QuestionOutSchema):
    user: UserOutSchema
    answer_count: int
    tags: list[TagOutSchema]


class QuestionWithJoinsOutSchema(QuestionOutSchema):
    user: UserOutSchema
    answers: list[AnswerWithCommentsOutSchema]
    comments: list[CommentOutSchema]
    tags: list[TagOutSchema]
