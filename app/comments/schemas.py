from pydantic import BaseModel, ConfigDict, model_validator, model_serializer, \
    Field
from typing_extensions import Self

from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.users.schemas import UserOutSchema


class CommentBaseSchema(BaseModel):
    body: str = Field(min_length=10, max_length=350)

    model_config = ConfigDict(from_attributes=True)


class CommentCreateSchema(CommentBaseSchema):
    question_id: int | None = None
    answer_id: int | None = None

    @model_validator(mode='after')
    def validate_question_or_answer(self) -> Self:
        if not self.question_id and not self.answer_id:
            raise ValueError(
                "Comment must be associated with a question or answer."
            )
        if self.question_id and self.answer_id:
            raise ValueError(
                "Comment cannot be associated with both a question and an answer."
            )
        return self


class CommentCreatePayloadSchema(CommentCreateSchema):
    user_id: int


class CommentUpdateSchema(CommentBaseSchema):
    body: str = Field(None, min_length=10, max_length=350)


class CommentOutSchema(CommentBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    user_id: int
    question_id: int | None
    answer_id: int | None

    @model_serializer(when_used='json')
    def to_json(self):
        return {
            'id': self.id,
            'body': self.body,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'answer_id': self.answer_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class CommentWithUserOutSchema(CommentOutSchema):
    user: UserOutSchema

    @model_serializer(when_used='json')
    def to_json(self):
        base_json = super().to_json()
        base_json['user'] = self.user
        return base_json
