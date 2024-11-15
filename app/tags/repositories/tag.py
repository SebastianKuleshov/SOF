from sqlalchemy import select, func, case, desc, Sequence
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.sql.functions import coalesce

from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionTagModel
from app.tags.models import TagModel


class TagRepository(BaseRepository):
    model = TagModel

    async def get_top_tags(
            self
    ) -> Sequence[TagModel]:
        question_tag_subquery = (
            select(
                QuestionTagModel.tag_id,
                func.count(QuestionTagModel.question_id).label(
                    'question_count'
                ),
                func.sum(
                    case(
                        (QuestionTagModel.created_at >= func.now() -
                         func.cast(func.concat(12, ' HOURS'), INTERVAL), 1),
                        else_=0
                    )
                ).label('questions_count_12h'),
                func.sum(
                    case(
                        (QuestionTagModel.created_at >= func.now() -
                         func.cast(func.concat(1.5, ' HOURS'), INTERVAL), 1),
                        else_=0
                    )
                ).label('questions_count_1_5h')
            ).select_from(
                QuestionTagModel
            ).group_by(QuestionTagModel.tag_id).subquery()
        )

        stmt = (
            select(
                self.model.name,
                coalesce(question_tag_subquery.c.question_count, 0).label(
                    'question_count'
                ),
                coalesce(question_tag_subquery.c.questions_count_12h, 0).label(
                    'questions_count_12h'
                ),
                coalesce(
                    question_tag_subquery.c.questions_count_1_5h, 0
                ).label(
                    'questions_count_1_5h'
                )
            ).outerjoin(
                question_tag_subquery,
                self.model.id == question_tag_subquery.c.tag_id
            ).where(
                coalesce(question_tag_subquery.c.question_count, 0) > 5
            ).order_by(
                desc(
                    coalesce(
                        question_tag_subquery.c.question_count, 0
                    )
                ),
                desc(
                    coalesce(
                        question_tag_subquery.c.questions_count_12h, 0
                    )
                )
            )
        )

        tags = await self.session.execute(stmt)
        return tags.unique().all()
