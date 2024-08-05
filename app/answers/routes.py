from typing import Annotated

from fastapi import APIRouter, Depends

from app.answers import schemas as answer_schemas
from app.answers.services import AnswerService
from app.auth.services import AuthService
from app.votes import schemas as vote_schemas
from app.votes.services.vote import VoteService

router = APIRouter(
    prefix='/answers',
    tags=['answers']
)


@router.post('/', response_model=answer_schemas.AnswerOutSchema)
async def create_answer(
        answer_service: Annotated[AnswerService, Depends()],
        answer: answer_schemas.AnswerCreateSchema,
        user: Annotated[AuthService.get_user_from_jwt, Depends()]
):
    return await answer_service.create_answer(answer, user.id)


@router.post(
    '/votes/upvote'
)
async def upvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        vote: vote_schemas.VoteCreateSchema,
) -> vote_schemas.VoteOutSchema:
    return await vote_service.create_vote(
        vote,
        'answer',
        user.id,
        True
    )


@router.post(
    '/votes/downvote'
)
async def downvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        vote: vote_schemas.VoteCreateSchema,
) -> vote_schemas.VoteOutSchema:
    return await vote_service.create_vote(
        vote,
        'answer',
        user.id,
        False
    )


@router.delete(
    '/votes/revoke-upvote'
)
async def revoke_upvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int,
) -> bool:
    return await vote_service.revoke_vote(
        'answer',
        answer_id,
        user.id,
        True
    )


@router.delete(
    '/votes/revoke-downvote'
)
async def revoke_downvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int,
) -> bool:
    return await vote_service.revoke_vote(
        'answer',
        answer_id,
        user.id,
        False
    )


@router.get(
    '/',
    response_model=list[answer_schemas.AnswerOutSchema]
)
async def get_answers(
        answer_service: Annotated[AnswerService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await answer_service.answer_repository.get_multi(
        skip,
        limit
    )


@router.get(
    '/{answer_id}',
    response_model=answer_schemas.AnswerWithJoinsOutSchema
)
async def get_answer(
        answer_service: Annotated[AnswerService, Depends()],
        answer_id: int
):
    return await answer_service.get_answer(answer_id)


@router.put(
    '/{answer_id}',
    response_model=answer_schemas.AnswerWithJoinsOutSchema
)
async def update_answer(
        answer_service: Annotated[AnswerService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int,
        answer: answer_schemas.AnswerUpdateSchema
):
    return await answer_service.update_answer(
        answer_id,
        user.id,
        answer
    )


@router.delete(
    '/{answer_id}'
)
async def delete_answer(
        answer_service: Annotated[AnswerService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int
) -> bool:
    return await answer_service.delete_answer(
        answer_id,
        user.id
    )
