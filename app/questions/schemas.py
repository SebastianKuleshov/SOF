from functools import cached_property
from typing import Text

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.answers.schemas import AnswerWithCommentsOutSchema
from app.comments.schemas import CommentOutSchema
from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.users.schemas import UserOutSchema
from app.votes.schemas import VoteOutSchema


class QuestionBaseSchema(BaseModel):
    title: str = Field(min_length=10, max_length=150)
    body: Text = Field(min_length=30, max_length=3500)

    model_config = ConfigDict(from_attributes=True)


class QuestionCreateSchema(QuestionBaseSchema):
    user_id: int


class QuestionCreatePayloadSchema(QuestionBaseSchema):
    tags: list[int] = Field(min_length=1, max_length=5)


class QuestionUpdateSchema(QuestionBaseSchema):
    title: str | None = Field(None, min_length=10, max_length=150)
    body: Text | None = Field(None, min_length=30, max_length=3500)
    accepted_answer_id: int | None = None


class QuestionUpdatePayloadSchema(QuestionUpdateSchema):
    tags: list[int] = Field(None, min_length=1, max_length=5)


class QuestionOutSchema(QuestionBaseSchema, CreatedAtUpdatedAtMixin):
    id: int
    user_id: int
    accepted_answer_id: int | None
    votes: list[VoteOutSchema] | None = Field(None, exclude=True)

    # Returns the difference of votes for the question.
    @computed_field
    @cached_property
    def votes_difference(self) -> int:
        if self.votes:
            upvotes = sum(vote.is_upvote for vote in self.votes)
            downvotes = len(self.votes) - upvotes
            return upvotes - downvotes
        return 0


class TagOutSchema(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class QuestionWithTagsOutSchema(QuestionOutSchema):
    tags: list[TagOutSchema]


class QuestionForListOutSchema(QuestionOutSchema):
    user: UserOutSchema
    answers: list[AnswerWithCommentsOutSchema] = Field(None, exclude=True)
    tags: list[TagOutSchema]

    # Returns the number of answers for the question.
    @computed_field
    @cached_property
    def answer_count(self) -> int:
        return len(self.answers)


class QuestionWithJoinsOutSchema(QuestionForListOutSchema):
    answers: list[AnswerWithCommentsOutSchema]
    comments: list[CommentOutSchema]
    current_user_id: int | None = Field(None, exclude=True)

    # Checks if the current user has voted on the question.
    # If the user has voted, it returns the VoteOutSchema.
    # If the user has not voted, it returns None.
    @computed_field
    @cached_property
    def current_user_vote(self) -> VoteOutSchema | None:
        vote_dict = {vote.user_id: vote for vote in self.votes}
        return vote_dict.get(self.current_user_id, None)
