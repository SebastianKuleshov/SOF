from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.answers import schemas as answer_schemas
from app.answers.services import AnswerService
from app.auth.services import AuthService
from app.voting.services.voting import VotingService

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
    '/votes/upvote/{answer_id}'
)
async def upvote_answer(
        voting_service: Annotated[VotingService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int
) -> JSONResponse:
    return await voting_service.upvote(
        'answer',
        answer_id,
        user.id
    )


@router.post(
    '/votes/downvote/{answer_id}'
)
async def downvote_answer(
        voting_service: Annotated[VotingService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int
) -> JSONResponse:
    return await voting_service.downvote(
        'answer',
        answer_id,
        user.id
    )


@router.post(
    '/votes/revoke-upvote/{answer_id}'
)
async def revoke_upvote_answer(
        voting_service: Annotated[VotingService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int
) -> JSONResponse:
    return await voting_service.revoke_upvote(
        'answer',
        answer_id,
        user.id
    )


@router.post(
    '/votes/revoke-downvote/{answer_id}'
)
async def revoke_downvote_answer(
        voting_service: Annotated[VotingService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_id: int
) -> JSONResponse:
    return await voting_service.revoke_downvote(
        'answer',
        answer_id,
        user.id
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


@router.post(
    '/votes'
)
async def get_votes(
        voting_service: Annotated[VotingService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        answer_ids: list[int]
) -> JSONResponse:
    return await voting_service.get_votes(
        'answer',
        answer_ids,
        user.id
    )


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
