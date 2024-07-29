from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel


class QuestionRepository(BaseRepository):
    model = QuestionModel

    def get_default_stmt(self) -> Select:
        return select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.answers).joinedload(
                AnswerModel.comments
            ),
            joinedload(self.model.comments)
        )

    async def get_multi_with_joins(
            self,
            filters: dict = None,
            offset: int = 0,
            limit: int = 100
    ) -> Sequence[QuestionModel]:
        stmt = select(self.model).options(
            joinedload(self.model.user),
            joinedload(self.model.answers)
        )
        if filters:
            stmt = stmt.filter_by(**filters)
        entities = await self.session.scalars(stmt.offset(offset).limit(limit))
        entities = entities.unique().all()
        return entities
