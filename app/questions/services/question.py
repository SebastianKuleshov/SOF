from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.common.services import SearchService
from app.common.services.aws_s3 import S3Service
from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionCreateSchema, \
    QuestionWithJoinsOutSchema, QuestionForListOutSchema, \
    QuestionWithTagsOutSchema, QuestionCreatePayloadSchema, \
    QuestionUpdatePayloadSchema, QuestionUpdateSchema
from app.tags.repositories import TagRepository
from app.users.repositories import UserRepository
from app.users.services import UserService


class QuestionService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            tag_repository: Annotated[TagRepository, Depends()],
            search_service: Annotated[SearchService, Depends()],
            user_service: Annotated[UserService, Depends()],
            s3_service: Annotated[S3Service, Depends()]
    ) -> None:
        self.question_repository = question_repository
        self.user_repository = user_repository
        self.answer_repository = answer_repository
        self.tag_repository = tag_repository
        self.search_service = search_service
        self.user_service = user_service
        self.s3_service = s3_service

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

        user_model = question.user
        avatar_url = await self.s3_service.generate_presigned_url(
            user_model.avatar_key
        ) if user_model.avatar_key else None
        user_schema = {
            **user_model.__dict__,
            'avatar_url': avatar_url
        }

        return QuestionWithJoinsOutSchema.model_validate(
            {
                **question.__dict__,
                'user': user_schema,
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
                {
                    **question.__dict__,
                    'user': {
                        **question.user.__dict__,
                        'avatar_url': await self.s3_service.generate_presigned_url(
                            question.user.avatar_key
                        ) if question.user.avatar_key else None
                    }

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

        user_permissions = await self.user_service.get_user_permissions(
            user_id
        )

        if question.user_id != user_id and 'update_any_question' not in user_permissions:
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
        user_permissions = await self.user_service.get_user_permissions(
            user_id
        )

        if question.user_id != user_id and 'delete_any_question' not in user_permissions:
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

        vote_difference_subquery = (
            await self.question_repository.get_vote_difference_subquery()
        )

        stmt = await self.question_repository.get_searching_stmt(
            vote_difference_subquery
        )

        for key, value in parsed_query.items():
            match key:
                case 'scores':
                    stmt = await (
                        self.question_repository.apply_scores_conditions(
                            stmt,
                            value,
                            vote_difference_subquery
                        )
                    )
                case 'strict_text':
                    stmt = await (
                        self.question_repository.apply_strict_conditions(
                            stmt,
                            value
                        )
                    )
                case 'tags':
                    stmt = await (
                        self.question_repository.apply_tags_conditions(
                            stmt,
                            value
                        )
                    )
                case 'users':
                    stmt = await (
                        self.question_repository.apply_users_conditions(
                            stmt,
                            value
                        )
                    )
                case 'dates':
                    stmt = await (
                        self.question_repository.apply_dates_conditions(
                            stmt,
                            value
                        )
                    )
                case 'booleans':
                    stmt = await (
                        self.question_repository.apply_booleans_conditions(
                            stmt,
                            value
                        )
                    )

        questions = await self.question_repository.fetch_questions_search(stmt)

        return [
            QuestionForListOutSchema.model_validate(
                question
            )
            for question in questions
        ]
