from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import Select, select, func, Subquery, case, and_, Sequence
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import joinedload

from app.answers.models import AnswerModel
from app.common.repositories.base_repository import BaseRepository
from app.questions.models import QuestionModel
from app.tags.models import TagModel
from app.votes.models import VotesModel


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

    async def get_vote_difference_subquery(
            self
    ) -> Subquery:
        vote_difference_subquery = (
            select(
                self.model.id.label('question_id'),
                func.sum(
                    case(
                        (VotesModel.is_upvote == True, 1),
                        (VotesModel.is_upvote == False, -1),
                        else_=0
                    )
                ).label('vote_difference')
            )
            .select_from(self.model)
            .outerjoin(VotesModel, VotesModel.question_id == self.model.id)
            .group_by(self.model.id)
            .subquery()
        )
        return vote_difference_subquery

    async def get_searching_stmt(
            self,
            vote_difference_subquery: Subquery
    ) -> Select:
        stmt = (
            select(self.model).options(
                joinedload(self.model.user),
                joinedload(self.model.tags),
                joinedload(self.model.votes)
            )
            .outerjoin(AnswerModel, AnswerModel.question_id == self.model.id)
            .outerjoin(
                vote_difference_subquery,
                vote_difference_subquery.c.question_id == self.model.id,
            )
        )
        return stmt

    @staticmethod
    async def apply_scores_conditions(
            stmt: Select,
            score_params: list,
            vote_difference_subquery: Subquery
    ) -> Select:
        score_conditions = []
        for param in score_params:
            if param['operator'] in ['..', '-']:
                if param['min_score']:
                    score_conditions.append(
                        vote_difference_subquery.c.vote_difference >= int(
                            param['min_score']
                        )
                    )
                if param['max_score']:
                    score_conditions.append(
                        vote_difference_subquery.c.vote_difference <= int(
                            param['max_score']
                        )
                    )
            else:
                score_conditions.append(
                    vote_difference_subquery.c.vote_difference >= int(
                        param['min_score']
                    )
                )

        return stmt.where(and_(*score_conditions))

    async def apply_strict_conditions(
            self,
            stmt: Select,
            strict_params: list
    ) -> Select:
        strict_conditions = []
        for field, term in strict_params:
            if field == "body":
                strict_conditions.append(self.model.body.ilike(f"%{term}%"))
            elif field == "title":
                strict_conditions.append(self.model.title.ilike(f"%{term}%"))
            elif field == "":
                strict_conditions.append(
                    func.concat(
                        self.model.title,
                        self.model.body,
                        AnswerModel.body
                    ).ilike(f"%{term}%")
                )
        return stmt.where(and_(*strict_conditions))

    async def apply_tags_conditions(
            self,
            stmt: Select,
            tags_params: list
    ) -> Select:
        tags_conditions = []
        for is_negative, tag in tags_params:
            condition = self.model.tags.any(
                TagModel.name.ilike(f"%{tag}%")
            )
            if is_negative:
                condition = ~condition
            tags_conditions.append(condition)

        return stmt.where(and_(*tags_conditions))

    async def apply_users_conditions(
            self,
            stmt: Select,
            users_params: list
    ) -> Select:
        users_conditions = [
            self.model.user_id == int(user_id)
            for user_id in users_params
        ]
        return stmt.where(and_(*users_conditions))

    @staticmethod
    async def __parse_date(
            date_str: str
    ) -> datetime:
        formats = ['%Y-%m-%d', '%Y-%m', '%Y']

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise HTTPException(
            status_code=400,
            detail='Invalid date format'
        )

    async def apply_dates_conditions(
            self,
            stmt: Select,
            date_params: tuple
    ) -> Select:
        date_conditions = []

        for date in date_params:
            field = (
                self.model.created_at if date['field'] == 'created'
                else self.model.updated_at
            )

            if date['operator']:
                date_conditions.append(
                    field.between(
                        await self.__parse_date(date['start_date']),
                        await self.__parse_date(date['end_date'])
                    )
                )
            else:
                date_conditions.append(
                    field >= await self.__parse_date(date['start_date'])
                )

        return stmt.where(and_(*date_conditions))

    async def apply_booleans_conditions(
            self,
            stmt: Select,
            boolean_params: list
    ) -> Select:
        boolean_conditions = []
        for field, value in boolean_params:
            if field == 'hasaccepted':
                boolean_conditions.append(
                    self.model.accepted_answer_id.isnot(None)
                    if value in ['true', 'yes', '1']
                    else self.model.accepted_answer_id.is_(None)
                )
            elif field == 'isanswered':
                boolean_conditions.append(
                    self.model.answers.any()
                    if value in ['true', 'yes', '1']
                    else ~self.model.answers.any()
                )

        return stmt.where(and_(*boolean_conditions))

    async def fetch_questions_search(
            self,
            stmt: Select
    ) -> Sequence[QuestionModel]:
        questions = await self.session.scalars(stmt)
        return questions.unique().all()

    async def get_questions_without_answer(
            self
    ) -> Sequence[QuestionModel]:
        questions_with_no_answers_subquery = (
            select(
                AnswerModel.question_id
            ).select_from(
                AnswerModel
            ).group_by(AnswerModel.question_id).subquery()
        )

        stmt = (
            select(
                self.model.id,
                self.model.title
            ).outerjoin(
                questions_with_no_answers_subquery,
                questions_with_no_answers_subquery.c.question_id == self.model.id
            ).where(
                and_(
                    questions_with_no_answers_subquery.c.question_id.is_(None),
                    self.model.created_at <= func.now() - func.cast(
                        func.concat(24, ' HOURS'), INTERVAL
                    )
                )
            ).order_by(self.model.created_at.desc())
        )

        unresolved_questions = await self.session.execute(stmt)
        return unresolved_questions.unique().all()

    async def get_questions_without_accepted_answer(
            self
    ) -> Sequence[QuestionModel]:
        stmt = (
            select(
                self.model.id,
                self.model.title
            )
            .where(
                and_(self.model.accepted_answer_id.is_(None)),
                self.model.created_at <= func.now() - func.cast(
                    func.concat(7, ' DAYS'), INTERVAL
                )
            )
        )

        unresolved_questions = await self.session.execute(stmt)
        return unresolved_questions.unique().all()
