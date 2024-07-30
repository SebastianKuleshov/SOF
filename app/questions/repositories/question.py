from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
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
        )

    async def attach_tags_to_question(
            self,
            question: QuestionModel,
            tags: Sequence[TagModel]
    ) -> None:
        question.tags = tags
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail="One of the tags already attached to the question."
            )

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
