from sqlalchemy import Select, select, func
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel, AnswerVoteModel
from app.common.repositories.base_repository import BaseRepository


class AnswerRepository(BaseRepository):
    model = AnswerModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.question)
        )

    async def get_user_vote(
            self,
            answer_id: int,
            user_id: int
    ) -> AnswerVoteModel | None:
        stmt = (
            select(AnswerVoteModel)
            .where(
                answer_id == AnswerVoteModel.answer_id,
                user_id == AnswerVoteModel.user_id
            )
        )
        answer_vote = await self.session.scalar(stmt)
        return answer_vote

    async def update_vote(
            self,
            answer_vote: AnswerVoteModel,
            is_upvote: bool
    ) -> None:
        answer_vote.is_upvote = is_upvote
        await self.session.commit()

    async def create_vote_answer(
            self,
            answer_id: int,
            user_id: int,
            is_upvote: bool
    ) -> None:
        answer_vote = AnswerVoteModel(
            answer_id=answer_id,
            user_id=user_id,
            is_upvote=is_upvote
        )
        self.session.add(answer_vote)
        await self.session.commit()

    async def get_answer_votes_difference(
            self,
            answer_id: int
    ) -> int:
        stmt = (
            select(
                AnswerVoteModel.is_upvote,
                func.count(AnswerVoteModel.is_upvote),
            )
            .where(answer_id == AnswerVoteModel.answer_id)
            .group_by(AnswerVoteModel.is_upvote)
            .order_by(AnswerVoteModel.is_upvote)
        )
        votes_count = await self.session.execute(stmt)
        votes_count = votes_count.all()
        votes_dict = dict(votes_count)

        upvotes = votes_dict.get(True, 0)
        downvotes = votes_dict.get(False, 0)

        difference = upvotes - downvotes
        return difference

