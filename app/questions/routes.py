from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.questions import schemas as question_schemas
from app.questions.services import QuestionService

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
        question: question_schemas.QuestionBaseSchema,
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        tags: list[int]
):
    return await question_service.create_question(question, user.id, tags)


@router.post(
    '/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def reattach_tags_to_question(
        question_service: Annotated[QuestionService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int,
        tags: list[int]
):
    return await question_service.reattach_tags_to_question(
        question_id,
        user.id,
        tags
    )


@router.post(
    '/votes/{question_id}',
    response_model=question_schemas.QuestionWithJoinsOutSchema
)
async def vote_question(
        question_service: Annotated[QuestionService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        question_id: int,
        is_upvote: bool
):
    return await question_service.vote_question(
        question_id,
        user.id,
        is_upvote
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
    '/user/{user_id}',
    response_model=list[question_schemas.QuestionForListOutSchema],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def get_questions_by_user(
        question_service: Annotated[QuestionService, Depends()],
        user_id: int
):
    return await question_service.get_questions_by_user(user_id)


@router.get(
    '/tag/{tag_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)],
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
        question: question_schemas.QuestionUpdateSchema
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
