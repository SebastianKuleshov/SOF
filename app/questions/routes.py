from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.questions import schemas as question_schemas
from app.questions.services import QuestionService
from app.votes import schemas as vote_schemas
from app.votes.services.vote import VoteService

public_router = APIRouter(
    prefix='/questions',
    tags=['questions']
)

private_router = APIRouter(
    prefix='/questions',
    tags=['questions'],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)


# Public routes

@public_router.get(
    '/',
    response_model=list[question_schemas.QuestionForListOutSchema]
)
async def get_questions(
        question_service: Annotated[QuestionService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await question_service.get_questions(
        skip,
        limit
    )


@public_router.get(
    '/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def get_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int
):
    return await question_service.get_question(question_id)


# Private routes

@private_router.post(
    '/',
    response_model=question_schemas.QuestionWithTagsOutSchema
)
async def create_question(
        question_service: Annotated[QuestionService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question: question_schemas.QuestionCreatePayloadSchema
):
    return await question_service.create_question(question, user_id)


@private_router.post(
    '/votes/upvote',
    response_model=vote_schemas.VoteOutSchema
)
async def upvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'question',
        user_id,
        True
    )


@private_router.post(
    '/votes/downvote',
    response_model=vote_schemas.VoteOutSchema
)
async def downvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'question',
        user_id,
        False
    )


@private_router.delete(
    '/votes/revoke-upvote'
)
async def revoke_upvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question_id: int
) -> bool:
    return await vote_service.revoke_vote(
        'question',
        question_id,
        user_id,
        True
    )


@private_router.delete(
    '/votes/revoke-downvote'
)
async def revoke_downvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question_id: int
) -> bool:
    return await vote_service.revoke_vote(
        'question',
        question_id,
        user_id,
        False
    )


@private_router.get(
    '/votes/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def get_question_with_user_vote(
        question_service: Annotated[QuestionService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question_id: int
):
    return await question_service.get_question(
        question_id,
        user_id
    )


@private_router.put(
    '/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def update_question(
        question_service: Annotated[QuestionService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question_id: int,
        question: question_schemas.QuestionUpdatePayloadSchema
):
    return await question_service.update_question(
        question_id,
        user_id,
        question
    )


@private_router.delete(
    '/{question_id}'
)
async def delete_question(
        question_service: Annotated[QuestionService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        question_id: int
) -> bool:
    return await question_service.delete_question(
        question_id,
        user_id
    )
