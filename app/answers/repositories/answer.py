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

    async def get_vote(
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

    async def create_vote(
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

    async def delete_vote(
            self,
            user_vote: AnswerVoteModel
    ) -> bool:
        await self.session.delete(user_vote)
        await self.session.commit()
        return True

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

    async def get_answers_votes_difference(
            self,
            answer_ids: list[int]
    ) -> dict[int, int]:
        stmt = (
            select(
                AnswerVoteModel.answer_id,
                AnswerVoteModel.is_upvote,
                func.count(AnswerVoteModel.is_upvote),
            )
            .where(AnswerVoteModel.answer_id.in_(answer_ids))
            .group_by(AnswerVoteModel.answer_id, AnswerVoteModel.is_upvote)
            .order_by(AnswerVoteModel.answer_id, AnswerVoteModel.is_upvote)
        )
        votes_count = await self.session.execute(stmt)
        votes_count = votes_count.all()

        votes_difference = {answer_id: 0 for answer_id in answer_ids}

        for answer_id, is_upvote, count in votes_count:
            if is_upvote:
                votes_difference[answer_id] += count
            else:
                votes_difference[answer_id] -= count

        return votes_difference

    async def get_votes(
            self,
            answer_ids: list[int],
            user_id: int
    ) -> dict[int, bool | None]:
        stmt = (
            select(AnswerVoteModel.answer_id, AnswerVoteModel.is_upvote)
            .where(
                AnswerVoteModel.answer_id.in_(answer_ids),
                user_id == AnswerVoteModel.user_id
            )
        )
        votes = await self.session.execute(stmt)
        votes = votes.all()

        return {
            answer_id: None for answer_id in answer_ids
        } | {
            vote.answer_id: vote.is_upvote for vote in votes
        }
