from typing import Annotated

from fastapi import Depends
from sqlalchemy import Select

from app.questions.repositories import QuestionRepository


class SearchQueryBuilder:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.vote_difference_subquery = None
        self.stmt = None

    async def initialize(
            self
    ) -> 'SearchQueryBuilder':
        self.vote_difference_subquery = (
            await self.question_repository.get_vote_difference_subquery()
        )
        self.stmt = await self.question_repository.get_searching_stmt(
            self.vote_difference_subquery
        )
        return self

    async def apply_scores_conditions(
            self,
            scores_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_scores_conditions(
            self.stmt,
            scores_query,
            self.vote_difference_subquery
        )
        return self

    async def apply_strict_conditions(
            self,
            strict_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_strict_conditions(
            self.stmt,
            strict_query
        )
        return self

    async def apply_tags_conditions(
            self,
            tags_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_tags_conditions(
            self.stmt,
            tags_query
        )
        return self

    async def apply_users_conditions(
            self,
            users_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_users_conditions(
            self.stmt,
            users_query
        )
        return self

    async def apply_dates_conditions(
            self,
            dates_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_dates_conditions(
            self.stmt,
            dates_query
        )
        return self

    async def apply_booleans_conditions(
            self,
            booleans_query
    ) -> 'SearchQueryBuilder':
        self.stmt = await self.question_repository.build_booleans_conditions(
            self.stmt,
            booleans_query
        )
        return self

    def get_statement(self) -> Select:
        return self.stmt
