from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import joinedload

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema, QuestionCreateSchema, \
    QuestionWithUserOutSchema, QuestionOutSchema, QuestionBaseSchema, \
    QuestionWithJoinsOutSchema
from app.users.repositories import UserRepository


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository
        self.answer_repository = answer_repository

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
        join_options = [
            joinedload(self.question_repository.model.user),
            joinedload(self.question_repository.model.answers).joinedload(
                self.answer_repository.model.comments
            ),
            joinedload(self.question_repository.model.comments)
        ]
        question = await self.question_repository.get_by_id_with_joins(
            question_id,
            join_options
        )
        if not question:
            raise HTTPException(status_code=404, detail='Question not found')
        return question

    async def get_questions(
            self,
            skip: int = 0,
            limit: int = 100
    ):
        join_options = [
            joinedload(self.question_repository.model.user),
            joinedload(self.question_repository.model.answers)
        ]
        return await self.question_repository.get_multi_with_joins(
            join_options,
            {},
            skip,
            limit
        )

    async def get_user_questions(
            self,
            user_id: int
    ) -> list[QuestionWithUserOutSchema]:
        await self.user_repository.get_entity_if_exists(user_id)
        join_options = [
            joinedload(self.question_repository.model.user)
        ]
        questions = await self.question_repository.get_multi_with_joins(
            join_options,
            {'user_id': user_id}
        )
        return [
            QuestionWithUserOutSchema.model_validate(question)
            for question in questions
        ]

    async def update_question(
            self,
            question_id: int,
            user_id: int,
            question_schema: QuestionUpdateSchema
    ) -> QuestionOutSchema:
        question = await self.question_repository.get_entity_if_exists(
            question_id
        )
        await self.answer_repository.get_entity_if_exists(
            question_schema.accepted_answer_id
        )
        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this question'
            )
        await self.question_repository.update(question_id, question_schema)
        await self.question_repository.expire_session_for_all()
        join_options = [
            joinedload(self.question_repository.model.user),
            joinedload(self.question_repository.model.answers).joinedload(
                self.answer_repository.model.comments
            ),
            joinedload(self.question_repository.model.comments)
        ]
        return await self.question_repository.get_by_id_with_joins(
            question_id,
            join_options
        )

    async def delete_question(
            self,
            question_id: int,
            user_id: int
    ) -> bool:
        question = await self.question_repository.get_entity_if_exists(
            question_id
        )
        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this question'
            )
        return await self.question_repository.delete(question_id)
