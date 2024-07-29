from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.answers.schemas import AnswerCreateSchema, AnswerUpdateSchema, \
    AnswerWithUserOutSchema, AnswerWithJoinsOutSchema, AnswerCreatePayloadSchema, \
    AnswerOutSchema
from app.questions.repositories import QuestionRepository
from app.users.repositories import UserRepository


class AnswerService:
    def __init__(
            self,
            answer_repository: Annotated[AnswerRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.answer_repository = answer_repository
        self.question_repository = question_repository
        self.user_repository = user_repository

    async def create_answer(
            self,
            answer_schema: AnswerCreateSchema,
            user_id: int
    ) -> AnswerOutSchema:
        answer_schema = AnswerCreatePayloadSchema(
            **answer_schema.model_dump(),
            user_id=user_id
        )
        await self.question_repository.check_question_exists(
            answer_schema.question_id
        )
        return await self.answer_repository.create(answer_schema)

    async def get_answer(
            self,
            answer_id: int
    ) -> AnswerWithJoinsOutSchema:
        answer = await self.answer_repository.get_by_id_with_joins(answer_id)
        if not answer:
            raise HTTPException(
                status_code=404,
                detail='Answer not found'
            )
        return answer

    async def update_answer(
            self,
            answer_id: int,
            user_id: int,
            answer_schema: AnswerUpdateSchema
    ) -> AnswerWithUserOutSchema:
        answer = await self.answer_repository.get_answer_if_exists(answer_id)
        if answer.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this answer'
            )
        await self.answer_repository.update(answer_id, answer_schema)
        return await self.answer_repository.get_by_id_with_user(answer_id)

    async def delete_answer(
            self,
            answer_id: int,
            user_id: int
    ) -> bool:
        answer = await self.answer_repository.get_answer_if_exists(answer_id)
        if answer.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this answer'
            )
        return await self.answer_repository.delete(answer_id)
