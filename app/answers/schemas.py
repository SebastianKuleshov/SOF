from typing import Text

from pydantic import BaseModel, Field, ConfigDict, model_serializer

from app.comments.schemas import CommentOutSchema
from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
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

    @model_serializer(when_used='json')
    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'body': self.body,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class AnswerWithUserOutSchema(AnswerOutSchema):
    user: UserOutSchema

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['user'] = self.user
        return base_json


class AnswerWithCommentsOutSchema(AnswerOutSchema):
    comments: list[CommentOutSchema]

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['comments'] = self.comments
        return base_json


class QuestionOutSchema(CreatedAtUpdatedAtMixin, BaseModel):
    id: int
    title: str
    body: Text
    user_id: int
    accepted_answer_id: int | None

    model_config = ConfigDict(from_attributes=True)

    @model_serializer(when_used='json')
    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body,
            'user_id': self.user_id,
            'accepted_answer_id': self.accepted_answer_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class AnswerWithJoinsOutSchema(AnswerOutSchema):
    user: UserOutSchema
    question: QuestionOutSchema

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['user'] = self.user
        base_json['question'] = self.question
        return base_json
