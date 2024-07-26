from typing import Text

from pydantic import BaseModel, ConfigDict, Field, model_serializer

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


class QuestionWithUserOutSchema(QuestionOutSchema):
    user: UserOutSchema

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['user'] = self.user
        return base_json


class QuestionForListOutSchema(QuestionOutSchema):
    user: UserOutSchema
    answer_count: int

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['answer_count'] = self.answer_count
        base_json['user'] = self.user
        return base_json


class AnswerOutSchema(CreatedAtUpdatedAtMixin, BaseModel):
    id: int
    user_id: int
    question_id: int
    body: Text = Field(min_length=30, max_length=3500)


class QuestionWithJoinsOutSchema(QuestionOutSchema):
    user: UserOutSchema
    answers: list[AnswerOutSchema] | None

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['user'] = self.user
        base_json['answers'] = self.answers
        return base_json
