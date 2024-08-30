from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self


class VoteBaseSchema(BaseModel):

    model_config = ConfigDict(from_attributes=True)


class VoteCreateSchema(VoteBaseSchema):
    question_id: int | None = None
    answer_id: int | None = None

    @model_validator(mode='after')
    def validate_question_or_answer(self) -> Self:
        if not self.question_id and not self.answer_id:
            raise ValueError(
                "Vote must be associated with a question or answer."
            )
        if self.question_id and self.answer_id:
            raise ValueError(
                "Vote cannot be associated with both a question and an answer."
            )
        return self


class VoteCreatePayloadSchema(VoteCreateSchema):
    user_id: str
    is_upvote: bool


class VoteOutSchema(VoteBaseSchema):
    id: int
    user_id: str
    question_id: int | None
    answer_id: int | None
    is_upvote: bool
