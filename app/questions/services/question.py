from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.questions.schemas import QuestionUpdateSchema, QuestionCreateSchema, \
    QuestionBaseSchema, \
    QuestionWithJoinsOutSchema, QuestionForListOutSchema, \
    QuestionWithTagsOutSchema
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
            question_schema: QuestionBaseSchema,
            user_id: int,
            tag_ids: list[int]
    ) -> QuestionWithTagsOutSchema:
        question_schema = QuestionCreateSchema(
            **question_schema.model_dump(),
            user_id=user_id
        )
        question_model = await self.question_repository.create(question_schema)

        tags = await self.tag_repository.get_entities_if_exists(tag_ids)
        await self.question_repository.attach_tags_to_question(
            question_model,
            tags
        )

        return QuestionWithTagsOutSchema.model_validate(question_model)

    async def reattach_tags_to_question(
            self,
            question_id: int,
            user_id: int,
            tag_ids: list[int]
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        if not question:
            raise HTTPException(
                status_code=404,
                detail='Question not found'
            )
        if question.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to attach tags to this question'
            )

        tags = await self.tag_repository.get_entities_if_exists(tag_ids)
        question = await self.question_repository.reattach_tags_to_question(
            question,
            tags
        )
        return QuestionWithJoinsOutSchema.model_validate(question)

    async def vote_question(
            self,
            question_id: int,
            user_id: int,
            is_upvote: bool
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_entity_if_exists(
            question_id
        )
        if question.user_id == user_id:
            raise HTTPException(
                status_code=400,
                detail='You are not allowed to vote your own question'
            )
        question_vote = await self.question_repository.get_user_vote(
            question_id,
            user_id
        )
        if question_vote:
            if question_vote.is_upvote == is_upvote:
                raise HTTPException(
                    status_code=400,
                    detail='You have already voted'
                )
            await self.question_repository.update_vote(
                question_vote,
                is_upvote
            )
        else:
            await self.question_repository.vote_question(
                question_id,
                user_id,
                is_upvote
            )

        await self.question_repository.expire_session_for_all()
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        return QuestionWithJoinsOutSchema.model_validate(question)

    async def get_question(
            self,
            question_id: int
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_by_id_with_joins(
            question_id
        )
        if not question:
            raise HTTPException(status_code=404, detail='Question not found')
        votes_difference = await self.question_repository.get_question_votes_difference(
            question_id
        )
        return QuestionWithJoinsOutSchema.model_validate(
            {
                **question.__dict__,
                'votes_difference': votes_difference
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
        questions_list = []
        for question in questions:
            votes_difference = await self.question_repository.get_question_votes_difference(
                question.id
            )
            questions_list.append(
                QuestionForListOutSchema.model_validate(
                    {
                        **question.__dict__,
                        'answer_count': len(question.answers),
                        'votes_difference': votes_difference
                    }
                )
            )
        return questions_list

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
            question_schema: QuestionUpdateSchema
    ) -> QuestionWithJoinsOutSchema:
        question = await self.question_repository.get_entity_if_exists(
            question_id
        )
        if question_schema.accepted_answer_id is not None:
            answer = await self.answer_repository.get_entity_if_exists(
                question_schema.accepted_answer_id
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
        await self.question_repository.update(question_id, question_schema)
        await self.question_repository.expire_session_for_all()
        question = await self.question_repository.get_by_id_with_joins(
            question_id
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
