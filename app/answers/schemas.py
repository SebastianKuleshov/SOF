from functools import cached_property
from typing import Text

from pydantic import BaseModel, Field, ConfigDict, computed_field

from app.comments.schemas import CommentOutSchema
from app.common.schemas_mixins import CreatedAtUpdatedAtMixin
from app.users.schemas import UserOutSchema
from app.votes.schemas import VoteOutSchema


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
    votes: list[VoteOutSchema] | None = Field(None, exclude=True)

    @computed_field
    @cached_property
    def votes_difference(self) -> int:
        if self.votes:
            upvotes = sum(vote.is_upvote for vote in self.votes)
            downvotes = len(self.votes) - upvotes
            return upvotes - downvotes
        return 0


class AnswerWithCommentsOutSchema(AnswerOutSchema):
    comments: list[CommentOutSchema]
    current_user_id: int | None = Field(None, exclude=True)

    @computed_field
    @cached_property
    def user_vote(self) -> VoteOutSchema | None:
        vote_dict = {vote.user_id: vote for vote in self.votes}
        return vote_dict.get(self.current_user_id, None)


class AnswerWithJoinsOutSchema(AnswerOutSchema):
    user: UserOutSchema
