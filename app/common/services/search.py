import re
from typing import Annotated

from fastapi import Depends
from sqlalchemy import and_

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionForListOutSchema
from app.votes.repository import VoteRepository


class SearchService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            vote_repository: Annotated[VoteRepository, Depends()]
    ):
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.vote_repository = vote_repository

    @staticmethod
    async def __parse_query(
            query: str
    ) -> dict:
        patterns = {
            "tags": r"(-)?\[(.*?)]",
            "strict": r"(title|body)?:?\"(.*?)\"",
            "score": r"score:(-?\d+)?(-|\.\.)?(-?\d+)?",
            "user": r"user:(\d+)",
            "dates": r"(created|lastactive):(\d{4}(?:-\d{2}(?:-\d{2})?)?)(\.\.)?(\d{4}(?:-\d{2}(?:-\d{2})?)?)?",
            'booleans': r"(hasaccepted|isanswered):(true|false|yes|no|1|0)"
        }

        tags_regex = re.compile(patterns["tags"])
        tags = tags_regex.findall(query)

        strict_regex = re.compile(patterns["strict"])
        strict_text = strict_regex.findall(query)

        score_regex = re.compile(patterns["score"])
        scores = score_regex.findall(query)

        user_regex = re.compile(patterns["user"])
        users = user_regex.findall(query)

        date_regex = re.compile(patterns["dates"])
        date = date_regex.findall(query)

        boolean_regex = re.compile(patterns["booleans"])
        booleans = boolean_regex.findall(query)

        for pattern in patterns.values():
            query = re.sub(pattern, "", query)

        plain_text = query.strip()

        return {
            "tags": tags,
            "strict_text": strict_text,
            "scores": scores,
            "plain_text": plain_text,
            "users": users,
            "dates": date,
            "booleans": booleans
        }

    async def search(
            self,
            query: str
    ) -> list[QuestionForListOutSchema]:
        parsed_query = await self.__parse_query(query)

        vote_difference_subquery = (
            await self.question_repository.get_vote_difference_subquery()
        )

        stmt = await self.question_repository.get_searching_stmt(
            vote_difference_subquery
        )

        conditions_map = {
            'scores':
                lambda
                    scores_query: self.question_repository.build_scores_conditions(
                    scores_query, vote_difference_subquery
                ),
            'strict_text': self.question_repository.build_strict_conditions,
            'tags': self.question_repository.build_tags_conditions,
            'users': self.question_repository.build_users_conditions,
            'dates': self.question_repository.build_dates_conditions,
            'booleans': self.question_repository.build_booleans_conditions
        }

        for key, build_conditions in conditions_map.items():
            if parsed_query.get(key):
                conditions = await build_conditions(parsed_query[key])
                stmt = stmt.where(and_(*conditions))

        questions = await self.question_repository.fetch_questions_search(stmt)

        return [
            QuestionForListOutSchema.model_validate(
                question
            )
            for question in questions
        ]
