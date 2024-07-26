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
    response_model=question_schemas.QuestionOutSchema
)
async def create_question(
        question_service: Annotated[QuestionService, Depends()],
        question: question_schemas.QuestionBaseSchema,
        user: Annotated[AuthService.get_user_from_jwt, Depends()]
):
    return await question_service.create_question(question, user.id)


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
    response_model=list[question_schemas.QuestionWithUserOutSchema],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def get_user_questions(
        question_service: Annotated[QuestionService, Depends()],
        user_id: int
):
    return await question_service.get_user_questions(user_id)


@router.put(
    '/{question_id}',
    response_model=question_schemas.QuestionOutSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def update_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int,
        question: question_schemas.QuestionUpdateSchema
):
    return await question_service.update_question(
        question_id,
        question
    )


@router.delete(
    '/{question_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def delete_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int
) -> bool:
    return await question_service.delete_question(question_id)
