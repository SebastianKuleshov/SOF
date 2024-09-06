from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from app.answers.repositories import AnswerRepository
from app.answers.schemas import AnswerCreateSchema, AnswerUpdateSchema, \
    AnswerWithJoinsOutSchema, \
    AnswerCreatePayloadSchema, \
    AnswerOutSchema
from app.questions.repositories import QuestionRepository
from app.users.repositories import UserRepository
from app.users.services import UserService


class AnswerService:
    def __init__(
            self,
            answer_repository: Annotated[AnswerRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            user_service: Annotated[UserService, Depends()]
    ) -> None:
        self.answer_repository = answer_repository
        self.question_repository = question_repository
        self.user_repository = user_repository
        self.user_service = user_service

    async def create_answer(
            self,
            answer_schema: AnswerCreateSchema,
            user_id: int
    ) -> AnswerOutSchema:
        answer_schema = AnswerCreatePayloadSchema(
            **answer_schema.model_dump(),
            user_id=user_id
        )
        await self.question_repository.get_entity_if_exists(
            answer_schema.question_id
        )
        try:
            return await self.answer_repository.create(answer_schema)
        except IntegrityError:
            raise HTTPException(
                status_code=400,
                detail='You have already answered this question'
            )

    async def update_answer(
            self,
            answer_id: int,
            user_id: int,
            answer_schema: AnswerUpdateSchema
    ) -> AnswerWithJoinsOutSchema:
        answer = await self.answer_repository.get_entity_if_exists(answer_id)
        user_permissions = await self.user_service.get_user_permissions(
            user_id
        )
        if answer.user_id != user_id and 'update_any_answer' not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this answer'
            )
        await self.answer_repository.update(answer_id, answer_schema)
        await self.answer_repository.expire_session_for_all()
        answer = await self.answer_repository.get_by_id_with_joins(
            answer_id
        )

        return AnswerWithJoinsOutSchema.model_validate(
            answer
        )

    async def delete_answer(
            self,
            answer_id: int,
            user_id: int
    ) -> bool:
        answer = await self.answer_repository.get_entity_if_exists(answer_id)
        user_permissions = await self.user_service.get_user_permissions(
            user_id
        )
        if answer.user_id != user_id and 'delete_any_answer' not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this answer'
            )
        return await self.answer_repository.delete(answer_id)
