import re
from typing import Annotated

from fastapi import Depends

from app.answers.repositories import AnswerRepository
from app.common.constants import PATTERNS
from app.questions.repositories import QuestionRepository
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
    async def parse_query(
            query: str
    ) -> dict:

        tags_regex = re.compile(PATTERNS["tags"])
        tags = tags_regex.findall(query)

        strict_regex = re.compile(PATTERNS["strict"])
        strict_text = strict_regex.findall(query)

        score_regex = re.compile(PATTERNS["score"])
        # Extracting the named groups (min_score, operator, max_score)
        # from each match
        scores = [match for match in score_regex.finditer(query)]

        user_regex = re.compile(PATTERNS["user"])
        users = user_regex.findall(query)

        date_regex = re.compile(PATTERNS["dates"])
        # Extracting the named groups (field, start_date, operator, end_date)
        # from each match
        date = [match for match in date_regex.finditer(query)]

        boolean_regex = re.compile(PATTERNS["booleans"])
        booleans = boolean_regex.findall(query)

        for pattern in PATTERNS.values():
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
