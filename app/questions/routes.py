from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.questions import schemas as question_schemas
from app.questions.services import QuestionService
from app.votes import schemas as vote_schemas
from app.votes.services.vote import VoteService

router = APIRouter(
    prefix='/questions',
    tags=['questions']
)


@router.post(
    '/',
    response_model=question_schemas.QuestionWithTagsOutSchema
)
async def create_question(
        question_service: Annotated[QuestionService, Depends()],
        question: question_schemas.QuestionCreatePayloadSchema,
        user: Annotated[AuthService.get_user_from_jwt, Depends()]
):
    return await question_service.create_question(question, user.id)


@router.post(
    '/votes/upvote',
    response_model=vote_schemas.VoteOutSchema
)
async def upvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'question',
        user.id,
        True
    )


@router.post(
    '/votes/downvote',
    response_model=vote_schemas.VoteOutSchema
)
async def downvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        vote: vote_schemas.VoteCreateSchema,
):
    return await vote_service.create_vote(
        vote,
        'question',
        user.id,
        False
    )


@router.delete(
    '/votes/revoke-upvote'
)
async def revoke_upvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int
) -> bool:
    return await vote_service.revoke_vote(
        'question',
        question_id,
        user.id,
        True
    )


@router.delete(
    '/votes/revoke-downvote'
)
async def revoke_downvote_question(
        vote_service: Annotated[VoteService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int
) -> bool:
    return await vote_service.revoke_vote(
        'question',
        question_id,
        user.id,
        False
    )


@router.get(
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


@router.get(
    '/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def get_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int
):
    return await question_service.get_question(question_id)


@router.get(
    '/votes/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def get_question_with_user_vote(
        question_service: Annotated[QuestionService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int
):
    return await question_service.get_question(
        question_id,
        user.id
    )


@router.get(
    '/user/{user_id}',
    response_model=list[question_schemas.QuestionForListOutSchema]
)
async def get_questions_by_user(
        question_service: Annotated[QuestionService, Depends()],
        user_id: int
):
    return await question_service.get_questions_by_user(user_id)


@router.get(
    '/tag/{tag_id}',
    response_model=list[question_schemas.QuestionForListOutSchema]
)
async def get_questions_by_tag(
        question_service: Annotated[QuestionService, Depends()],
        tag_id: int
):
    return await question_service.get_questions_by_tag(
        tag_id
    )


@router.put(
    '/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def update_question(
        question_service: Annotated[QuestionService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int,
        question: question_schemas.QuestionUpdatePayloadSchema
):
    return await question_service.update_question(
        question_id,
        user.id,
        question
    )


@router.delete(
    '/{question_id}'
)
async def delete_question(
        question_service: Annotated[QuestionService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int
) -> bool:
    return await question_service.delete_question(
        question_id,
        user.id
    )
