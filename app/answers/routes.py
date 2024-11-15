from typing import Annotated

from fastapi import APIRouter, Depends

from app.answers import schemas as answer_schemas
from app.answers.services import AnswerService
from app.auth.services import AuthService
from app.votes import schemas as vote_schemas
from app.votes.services.vote import VoteService

router = APIRouter(
    prefix='/answers',
    tags=['answers'],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)


@router.post(
    '/',
    response_model=answer_schemas.AnswerOutSchema,
    dependencies=[Depends(AuthService.require_permissions({'create_own_answer'}))]
)
async def create_answer(
        answer_service: Annotated[AnswerService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        answer: answer_schemas.AnswerCreateSchema
):
    return await answer_service.create_answer(answer, user_id)


@router.post(
    '/votes/upvote',
    response_model=vote_schemas.VoteOutSchema,
    dependencies=[Depends(AuthService.require_permissions({'upvote'}))]
)
async def upvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'answer',
        user_id,
        True
    )


@router.post(
    '/votes/downvote',
    response_model=vote_schemas.VoteOutSchema,
    dependencies=[Depends(AuthService.require_permissions({'downvote'}))]
)
async def downvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'answer',
        user_id,
        False
    )


@router.delete(
    '/votes/revoke-upvote',
    dependencies=[Depends(AuthService.require_permissions({'upvote'}))]
)
async def revoke_upvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        answer_id: int,
) -> bool:
    return await vote_service.revoke_vote(
        'answer',
        answer_id,
        user_id,
        True
    )


@router.delete(
    '/votes/revoke-downvote',
    dependencies=[Depends(AuthService.require_permissions({'downvote'}))]
)
async def revoke_downvote_answer(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        answer_id: int,
) -> bool:
    return await vote_service.revoke_vote(
        'answer',
        answer_id,
        user_id,
        False
    )


@router.put(
    '/{answer_id}',
    response_model=answer_schemas.AnswerWithJoinsOutSchema,
    dependencies=[Depends(AuthService.require_permissions({'update_own_answer'}))]
)
async def update_answer(
        answer_service: Annotated[AnswerService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        answer_id: int,
        answer: answer_schemas.AnswerUpdateSchema
):
    return await answer_service.update_answer(
        answer_id,
        user_id,
        answer
    )


@router.delete(
    '/{answer_id}',
    dependencies=[Depends(AuthService.require_permissions({'delete_own_answer'}))]
)
async def delete_answer(
        answer_service: Annotated[AnswerService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        answer_id: int
) -> bool:
    return await answer_service.delete_answer(
        answer_id,
        user_id
    )
