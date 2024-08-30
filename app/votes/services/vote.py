from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository
from app.users.repositories import UserRepository
from app.users.services import UserService
from app.votes.repository import VoteRepository
from app.votes.schemas import VoteCreateSchema, VoteCreatePayloadSchema, \
    VoteOutSchema


class VoteService:
    def __init__(
            self,
            vote_repository: Annotated[VoteRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            user_repository: Annotated[UserRepository, Depends()],
            user_service: Annotated[UserService, Depends()]
    ) -> None:
        self.vote_repository = vote_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.user_repository = user_repository
        self.user_service = user_service

    async def __get_entity_repository(
            self,
            entity_type: str
    ) -> QuestionRepository | AnswerRepository:
        if entity_type == 'question':
            return self.question_repository
        elif entity_type == 'answer':
            return self.answer_repository
        else:
            raise HTTPException(
                status_code=400,
                detail='Invalid entity type'
            )

    async def create_vote(
            self,
            vote_schema: VoteCreateSchema,
            entity_type: str,
            user_id: str,
            is_upvote: bool
    ) -> VoteOutSchema:
        repository = await self.__get_entity_repository(entity_type)

        entity_id = vote_schema.model_dump().get(f'{entity_type}_id')
        entity = await repository.get_entity_if_exists(entity_id)

        if entity.user_id == user_id:
            raise HTTPException(
                status_code=403,
                detail=f'You are not allowed to vote your own {entity_type}'
            )

        existing_vote = await self.vote_repository.get_one(
            {
                'user_id': user_id,
                f'{entity_type}_id': entity_id
            }
        )
        target_user_id = entity.user_id

        if existing_vote:
            raise HTTPException(
                status_code=400,
                detail=f'You have already voted on this {entity_type}'
            )

        vote_model = await self.vote_repository.create(
            VoteCreatePayloadSchema(
                **vote_schema.__dict__,
                user_id=user_id,
                is_upvote=is_upvote
            )
        )

        user_reputation = await self.user_repository.update_reputation(
            target_user_id,
            is_upvote
        )

        if user_reputation == 100 and is_upvote:
            await self.user_service.check_and_update_user_role(
                target_user_id,
                True
            )
        elif user_reputation == 99 and not is_upvote:
            await self.user_service.check_and_update_user_role(
                target_user_id,
                False
            )

        return VoteOutSchema.model_validate(vote_model)

    async def revoke_vote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: str,
            is_upvote: bool
    ) -> bool:
        repository = await self.__get_entity_repository(entity_type)
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

        entity = await repository.get_entity_if_exists(entity_id)
        target_user_id = entity.user_id

        user_reputation = await self.user_repository.update_reputation(
            target_user_id,
            not is_upvote
        )

        if user_reputation == 99 and is_upvote:
            await self.user_service.check_and_update_user_role(
                target_user_id,
                False
            )
        elif user_reputation == 100 and not is_upvote:
            await self.user_service.check_and_update_user_role(
                target_user_id,
                True
            )

        return await self.vote_repository.delete(vote.id)
