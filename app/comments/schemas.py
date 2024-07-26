from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


class CommentBaseSchema(BaseModel):
    body: str

    model_config = ConfigDict(from_attributes=True)


class CommentCreateSchema(CommentBaseSchema):
    user_id: int
    question_id: int
    answer_id: int

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


class CommentUpdateSchema(CommentBaseSchema):
    body: str = None
