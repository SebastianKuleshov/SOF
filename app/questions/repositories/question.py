from datetime import datetime
from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import Select, select, func, Subquery, case
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
        stmt = self._get_default_stmt()
        stmt = (
            stmt
            .outerjoin(AnswerModel, AnswerModel.question_id == self.model.id)
            .outerjoin(
                vote_difference_subquery,
                vote_difference_subquery.c.question_id == self.model.id,
            )
        )
        return stmt

    @staticmethod
    async def build_scores_conditions(
            score_params: list,
            vote_difference_subquery: Subquery
    ) -> list:
        score_conditions = []
        for score in score_params:
            if score[1] == '..' or score[1] == '-':
                if score[0]:
                    score_conditions.append(
                        vote_difference_subquery.c.vote_difference >= int(
                            score[0]
                        )
                    )
                if score[2]:
                    score_conditions.append(
                        vote_difference_subquery.c.vote_difference <= int(
                            score[2]
                        )
                    )
            else:
                score_conditions.append(
                    vote_difference_subquery.c.vote_difference >= int(score[0])
                )

        return score_conditions

    async def build_strict_conditions(
            self,
            strict_params: list
    ) -> list:
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
        return strict_conditions

    async def build_tags_conditions(
            self,
            tags_params: list
    ) -> list:
        tags_conditions = []
        for is_negative, tag in tags_params:
            condition = self.model.tags.any(
                TagModel.name.ilike(f"%{tag}%")
            )
            if is_negative:
                condition = ~condition
            tags_conditions.append(condition)

        return tags_conditions

    async def build_users_conditions(
            self,
            users_params: list
    ) -> list:
        users_conditions = [
            self.model.user_id == int(user_id)
            for user_id in users_params
        ]
        return users_conditions

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

    async def build_dates_conditions(
            self,
            date_params: tuple
    ) -> list:
        date_conditions = []

        for date in date_params:
            field = (
                self.model.created_at if date[0] == 'created'
                else self.model.updated_at
            )

            if date[2]:
                date_conditions.append(
                    field.between(
                        await self.__parse_date(date[1]),
                        await self.__parse_date(date[3])
                    )
                )
            else:
                date_conditions.append(
                    field >= await self.__parse_date(date[1])
                )

        return date_conditions

    async def build_booleans_conditions(
            self,
            boolean_params: list
    ) -> list:
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

        return boolean_conditions

    async def fetch_questions_search(
            self,
            stmt: Select
    ) -> Sequence[QuestionModel]:
        questions = await self.session.scalars(stmt)
        return questions.unique().all()
