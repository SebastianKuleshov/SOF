from typing import Annotated

from fastapi import Depends, HTTPException

from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema, QuestionCreateSchema, \
    QuestionWithUserOutSchema, QuestionOutSchema, QuestionBaseSchema, \
    QuestionWithJoinsOutSchema
from app.users.repositories import UserRepository


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository

    async def create_question(
            self,
            question_schema: QuestionBaseSchema,
            user_id: int
    ) -> QuestionOutSchema:
        question_schema = QuestionCreateSchema(
            **question_schema.model_dump(),
            user_id=user_id
        )
        question_model = await self.question_repository.create(question_schema)
        return QuestionOutSchema.model_validate(question_model)

    async def get_question(
            self,
            question_id: int
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        if not question:
            raise HTTPException(status_code=404, detail='Question not found')
        return question

    async def get_questions(
            self,
            skip: int = 0,
            limit: int = 100
    ):
        return await self.question_repository.get_list_with_joins(skip, limit)

    async def get_user_questions(
            self,
            user_id: int
    ) -> list[QuestionWithUserOutSchema]:
        await self.user_repository.get_user_if_exists(user_id)
        return await self.question_repository.get_user_questions(user_id)

    async def update_question(
            self,
            question_id: int,
            user_id: int,
            question_schema: QuestionUpdateSchema
    ) -> QuestionWithUserOutSchema:
        question = await self.question_repository.get_question_if_exists(
            question_id
        )
        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this question'
            )
        await self.question_repository.update(question_id, question_schema)
        await self.question_repository.expire_session_for_all()
        return await self.question_repository.get_question_by_id(question_id)

    async def delete_question(
            self,
            question_id: int,
            user_id: int
    ) -> bool:
        question = await self.question_repository.get_question_if_exists(
            question_id
        )
        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this question'
            )
        return await self.question_repository.delete(question_id)
