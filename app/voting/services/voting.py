from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.responses import JSONResponse

from app.answers.repositories import AnswerRepository
from app.questions.repositories import QuestionRepository


class VotingService:
    def __init__(
            self,
            question_repository: Annotated[QuestionRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
    ) -> None:
        self.question_repository = question_repository
        self.answer_repository = answer_repository

    async def _get_repository(
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

    async def upvote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        entity = await repository.get_entity_if_exists(entity_id)
        if entity.user_id == user_id:
            raise HTTPException(
                status_code=403,
                detail=f'You are not allowed to vote your own {entity_type}'
            )

        user_vote = await repository.get_vote(entity_id, user_id)
        if user_vote is not None:
            raise HTTPException(
                status_code=400,
                detail='You have already upvoted or downvoted'
            )
        await repository.create_vote(entity_id, user_id, True)

        return JSONResponse(
            content={"message": "Vote created"},
            status_code=201
        )

    async def downvote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        entity = await repository.get_entity_if_exists(entity_id)
        if entity.user_id == user_id:
            raise HTTPException(
                status_code=403,
                detail=f'You are not allowed to vote your own {entity_type}'
            )

        user_vote = await repository.get_vote(entity_id, user_id)
        if user_vote is not None:
            raise HTTPException(
                status_code=400,
                detail='You have already downvoted or upvoted'
            )
        await repository.create_vote(entity_id, user_id, False)

        return JSONResponse(
            content={"message": "Vote created"},
            status_code=201
        )

    async def revoke_upvote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        user_vote = await repository.get_vote(entity_id, user_id)
        if user_vote is None or not user_vote.is_upvote:
            raise HTTPException(
                status_code=400,
                detail='You have not upvoted'
            )
        await repository.delete_vote(user_vote)

        return JSONResponse(
            content={"message": "Vote deleted"},
            status_code=200
        )

    async def revoke_downvote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        user_vote = await repository.get_vote(entity_id, user_id)
        if user_vote is None or user_vote.is_upvote:
            raise HTTPException(
                status_code=400,
                detail='You have not downvoted'
            )
        await repository.delete_vote(user_vote)

        return JSONResponse(
            content={"message": "Vote deleted"},
            status_code=200
        )

    async def get_vote(
            self,
            entity_type: str,
            entity_id: int,
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        user_vote = await repository.get_vote(entity_id, user_id)
        return JSONResponse(
            content={"is_upvote": user_vote.is_upvote if user_vote else None},
            status_code=200
        )

    async def get_votes(
            self,
            entity_type: str,
            entity_ids: list[int],
            user_id: int
    ) -> JSONResponse:
        repository = await self._get_repository(entity_type)
        await repository.get_entities_if_exists(entity_ids)
        votes = await repository.get_votes(entity_ids, user_id)

        return JSONResponse(
            content={"votes": votes},
            status_code=200
        )
