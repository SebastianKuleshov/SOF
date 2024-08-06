from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel
from app.tags.models import TagModel


class QuestionRepository(BaseRepository):
    model = QuestionModel

    def _get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.answers),
            joinedload(self.model.tags),
            joinedload(self.model.votes)
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
            joinedload(self.model.answers).options(
                joinedload(
                    AnswerModel.comments
                ),
                joinedload(
                    AnswerModel.votes
                )
            ),
            joinedload(self.model.comments)
        )

        return await self.session.scalar(stmt.filter_by(id=question_id))
