from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.users.repositories import UserRepository
from app.votes.repository import VoteRepository
from app.votes.schemas import VoteCreateSchema, VoteCreatePayloadSchema


class VoteService:
    def __init__(
            self,
            vote_repository: Annotated[VoteRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.vote_repository = vote_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.user_repository = user_repository

    async def create_vote(
            self,
            vote_schema: VoteCreateSchema,
            user_id: int,
            is_upvote: bool
    ) -> JSONResponse:
        if vote_schema.question_id:
            question = await self.question_repository.get_entity_if_exists(
                vote_schema.question_id
            )
            if question.user_id == user_id:
                raise HTTPException(
                    status_code=403,
                    detail='You are not allowed to vote your own question'
                )

            existing_vote = await self.vote_repository.get_one(
                {
                    'user_id': user_id,
                    'question_id': vote_schema.question_id
                }
            )
            target_user_id = question.user_id

        elif vote_schema.answer_id:
            answer = await self.answer_repository.get_entity_if_exists(
                vote_schema.answer_id
            )
            if answer.user_id == user_id:
                raise HTTPException(
                    status_code=403,
                    detail='You are not allowed to vote your own answer'
                )

            existing_vote = await self.vote_repository.get_one(
                {
                    'user_id': user_id,
                    'answer_id': vote_schema.answer_id
                }
            )
            target_user_id = answer.user_id

        if existing_vote:
            raise HTTPException(
                status_code=400,
                detail='You have already voted on this item'
            )

        await self.vote_repository.create(
            VoteCreatePayloadSchema(
                **vote_schema.__dict__,
                user_id=user_id,
                is_upvote=is_upvote
            )
        )

        await self.user_repository.update_reputation(
            target_user_id,
            is_upvote
        )

        return JSONResponse(
            content={"message": "Vote created"},
            status_code=201
        )

    async def revoke_vote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int,
            is_upvote: bool
    ) -> JSONResponse:
        vote = await self.vote_repository.get_one(
            {
                'user_id': user_id,
                f'{entity_type}_id': entity_id,
                'is_upvote': is_upvote
            }
        )
        if not vote:
            raise HTTPException(
                status_code=404,
                detail='Vote not found'
            )

        if entity_type == 'question':
            question = await self.question_repository.get_entity_if_exists(
                entity_id
            )
            target_user_id = question.user_id
        elif entity_type == 'answer':
            answer = await self.answer_repository.get_entity_if_exists(
                entity_id
            )
            target_user_id = answer.user_id

        await self.vote_repository.delete(vote.id)

        await self.user_repository.update_reputation(
            target_user_id,
            not is_upvote
        )

        return JSONResponse(
            content={"message": "Vote deleted"},
            status_code=200
        )
