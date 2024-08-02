from typing import Sequence

from sqlalchemy import Select, select, delete
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel, QuestionVoteModel
from app.tags.models import TagModel


class QuestionRepository(BaseRepository):
    model = QuestionModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.answers),
            joinedload(self.model.tags),
        )

    async def attach_tags_to_question(
            self,
            question: QuestionModel,
            tags: Sequence[TagModel]
    ) -> None:
        question.tags = tags
        await self.session.commit()

    async def reattach_tags_to_question(
            self,
            question: QuestionModel,
            tags: Sequence[TagModel]
    ) -> None:
        question.tags.clear()
        await self.session.flush()
        question.tags = tags

        await self.session.commit()

    async def get_vote(
            self,
            question_id: int,
            user_id: int
    ) -> QuestionVoteModel | None:
        stmt = (
            select(QuestionVoteModel)
            .where(
                question_id == QuestionVoteModel.question_id,
                user_id == QuestionVoteModel.user_id
            )
        )
        question_vote = await self.session.scalar(stmt)
        return question_vote

    async def create_vote(
            self,
            question_id: int,
            user_id: int,
            is_upvote: bool
    ) -> None:
        question_vote = QuestionVoteModel(
            question_id=question_id,
            user_id=user_id,
            is_upvote=is_upvote
        )
        self.session.add(question_vote)
        await self.session.commit()

    async def delete_vote(
            self,
            user_vote: QuestionVoteModel
    ) -> bool:
        await self.session.delete(user_vote)
        await self.session.commit()

        return True

    async def get_question_votes_difference(
            self,
            question_id: int
    ) -> int:
        stmt = (
            select(
                QuestionVoteModel.is_upvote,
                func.count(QuestionVoteModel.is_upvote),
            )
            .where(question_id == QuestionVoteModel.question_id)
            .group_by(QuestionVoteModel.is_upvote)
            .order_by(QuestionVoteModel.is_upvote)
        )
        votes_count = await self.session.execute(stmt)
        votes_count = votes_count.all()
        votes_dict = dict(votes_count)

        upvotes = votes_dict.get(True, 0)
        downvotes = votes_dict.get(False, 0)

        difference = upvotes - downvotes
        return difference

    async def get_questions_by_tag(
            self,
            tag_id: int
    ) -> Sequence[QuestionModel]:
        stmt = (self._get_default_stmt()
                .join(self.model.tags)
                .where(tag_id == TagModel.id))
        questions = await self.session.scalars(stmt)
        questions = questions.unique().all()
        return questions

    async def get_by_id_with_joins(
            self,
            question_id: int
    ) -> QuestionModel:
        stmt = self._get_default_stmt().options(
            joinedload(self.model.answers).joinedload(
                AnswerModel.comments
            ),
            joinedload(self.model.comments)
        )

        return await self.session.scalar(stmt.filter_by(id=question_id))
