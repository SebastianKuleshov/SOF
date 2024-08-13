from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.common.services import SearchService
from app.questions.repositories import QuestionRepository, SearchQueryBuilder
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
            tag_repository: Annotated[TagRepository, Depends()],
            search_service: Annotated[SearchService, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository
        self.answer_repository = answer_repository
        self.tag_repository = tag_repository
        self.search_service = search_service

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
            question_id: int,
            user_id: int | None = None
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        if not question:
            raise HTTPException(status_code=404, detail='Question not found')

        # Checks if the current user has voted on the answers.
        answers_with_user_vote = question.answers
        if user_id:
            answers_with_user_vote = [
                {
                    **answer.__dict__,
                    'current_user_id': user_id
                } for answer in question.answers
            ]

        return QuestionWithJoinsOutSchema.model_validate(
            {
                **question.__dict__,
                'answers': answers_with_user_vote,
                'current_user_id': user_id
            }
        )

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
                question
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
        update_schema = QuestionUpdateSchema(
            **question_payload_schema.model_dump(exclude_unset=True)
        )

        await self.question_repository.update(
            question_id,
            update_schema
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

        return QuestionWithJoinsOutSchema.model_validate(
            question
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

    async def search(
            self,
            query: str
    ) -> list[QuestionForListOutSchema]:
        parsed_query = await self.search_service.parse_query(query)

        builder = await SearchQueryBuilder(
            self.question_repository
        ).initialize()

        for key, value in parsed_query.items():
            match key:
                case 'scores':
                    builder = await builder.apply_scores_conditions(value)
                case 'strict_text':
                    builder = await builder.apply_strict_conditions(value)
                case 'tags':
                    builder = await builder.apply_tags_conditions(value)
                case 'users':
                    builder = await builder.apply_users_conditions(value)
                case 'dates':
                    builder = await builder.apply_dates_conditions(value)
                case 'booleans':
                    builder = await builder.apply_booleans_conditions(value)

        stmt = builder.get_statement()

        questions = await self.question_repository.fetch_questions_search(stmt)

        return [
            QuestionForListOutSchema.model_validate(
                question
            )
            for question in questions
        ]
