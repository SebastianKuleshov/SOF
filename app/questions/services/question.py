from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionCreateSchema, \
    QuestionWithJoinsOutSchema, QuestionForListOutSchema, \
    QuestionWithTagsOutSchema, QuestionCreatePayloadSchema, \
    QuestionUpdatePayloadSchema, QuestionUpdateSchema
from app.tags.repositories import TagRepository
from app.users.repositories import UserRepository


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            tag_repository: Annotated[TagRepository, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository
        self.answer_repository = answer_repository
        self.tag_repository = tag_repository

    async def create_question(
            self,
            question_payload_schema: QuestionCreatePayloadSchema,
            user_id: int
    ) -> QuestionWithTagsOutSchema:
        question_create_schema = QuestionCreateSchema(
            **question_payload_schema.model_dump(),
            user_id=user_id
        )
        question_model = await self.question_repository.create(
            question_create_schema
        )

        tag_ids = question_payload_schema.tags
        tags = await self.tag_repository.get_entities_if_exists(tag_ids)
        await self.question_repository.attach_tags_to_question(
            question_model,
            tags
        )

        return QuestionWithTagsOutSchema.model_validate(question_model)

    async def get_question(
            self,
            question_id: int
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        if not question:
            raise HTTPException(status_code=404, detail='Question not found')
        return QuestionWithJoinsOutSchema.model_validate(question)

    async def get_questions(
            self,
            skip: int = 0,
            limit: int = 100
    ) -> list[QuestionForListOutSchema]:
        questions = await self.question_repository.get_multi_with_joins(
            {},
            skip,
            limit
        )
        return [
            QuestionForListOutSchema.model_validate(
                {
                    **question.__dict__,
                    'answer_count': len(question.answers)
                }
            )
            for question in questions
        ]

    async def get_questions_by_user(
            self,
            user_id: int
    ) -> list[QuestionForListOutSchema]:
        await self.user_repository.get_entity_if_exists(user_id)
        questions = await self.question_repository.get_multi_with_joins(
            {'user_id': user_id}
        )
        return [
            QuestionForListOutSchema.model_validate(
                {
                    **question.__dict__,
                    'answer_count': len(question.answers)
                }
            )
            for question in questions
        ]

    async def get_questions_by_tag(
            self,
            tag_id: int
    ) -> list[QuestionForListOutSchema]:
        questions = await self.question_repository.get_questions_by_tag(tag_id)
        return [
            QuestionForListOutSchema.model_validate(
                {
                    **question.__dict__,
                    'answer_count': len(question.answers)
                }
            )
            for question in questions
        ]

    async def update_question(
            self,
            question_id: int,
            user_id: int,
            question_payload_schema: QuestionUpdatePayloadSchema
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_entity_if_exists(
            question_id
        )
        if question_payload_schema.accepted_answer_id is not None:
            answer = await self.answer_repository.get_entity_if_exists(
                question_payload_schema.accepted_answer_id
            )
            if answer.question_id != question_id:
                raise HTTPException(
                    status_code=400,
                    detail='Answer does not belong to this question'
                )

        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this question'
            )
        await self.question_repository.update(
            question_id,
            QuestionUpdateSchema(**question_payload_schema.__dict__)
        )

        await self.question_repository.expire_session_for_all()
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )

        if question_payload_schema.tags is not None:
            tags = await self.tag_repository.get_entities_if_exists(
                question_payload_schema.tags
            )

            await self.question_repository.reattach_tags_to_question(
                question,
                tags
            )

        return QuestionWithJoinsOutSchema.model_validate(question)

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
