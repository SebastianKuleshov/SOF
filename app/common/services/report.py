import csv
from io import StringIO
from typing import Annotated

from fastapi import Depends

from app.questions.repositories import QuestionRepository
from app.tags.repositories import TagRepository
from app.users.repositories import UserRepository


class ReportService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()],
            tag_repository: Annotated[TagRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()]
    ) -> None:
        self.user_repository = user_repository
        self.tag_repository = tag_repository
        self.question_repository = question_repository

    async def generate_report(self):
        res = await self.user_repository.get_top_contributors()
        res2 = await self.tag_repository.get_top_tags()
        res3 = await self.question_repository.get_questions_with_no_answer()
        res4 = await self.question_repository.get_questions_with_no_accepted_answer()

        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Top Contributors'])
        csv_writer.writerow(
            [
                'User ID',
                'User nickname',
                'Total answers',
                'Answers amount within the last 24 hours',
                'Average answers amount per week',
                'Total answer upvotes',
                'Average upvotes per answer received',
                'Total answer downvotes',
                'Average downvotes per answer received'
            ]
        )
        for user in res:
            csv_writer.writerow(
                [
                    user[0], user[1], user[2], user[3],
                    user[4], user[5], user[6], user[7], user[8]
                ]
            )

        csv_file.seek(0)

        print()
        print(csv_file.getvalue())
        print()

        return res
