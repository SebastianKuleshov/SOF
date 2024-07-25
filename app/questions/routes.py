from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.questions import schemas
from app.questions.services import QuestionService

router = APIRouter(
    prefix='/questions',
    tags=['questions']
)


@router.post(
    '/',
    response_model=schemas.QuestionOutSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def create_question(
        question_service: Annotated[QuestionService, Depends()],
        question: schemas.QuestionCreateSchema
):
    return await question_service.question_repository.create(question)


@router.get('/', response_model=list[schemas.QuestionOutSchema])
async def get_questions(
        question_service: Annotated[QuestionService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await question_service.question_repository.get_multi(skip, limit)


@router.get(
    '/{question_id}',
    response_model=schemas.QuestionWithUserOutSchema
)
async def get_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int
):
    return await question_service.get_question(question_id)


@router.get(
    '/user/me',
    response_model=list[schemas.QuestionWithUserOutSchema]
)
async def get_user_questions(
        question_service: Annotated[QuestionService, Depends()],
        user_model: Annotated[AuthService.get_user_from_jwt, Depends()],
):
    return await question_service.question_repository.get_user_questions(
        user_model.id
    )


@router.get(
    '/user/{user_id}',
    response_model=list[schemas.QuestionWithUserOutSchema],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def get_user_questions(
        question_service: Annotated[QuestionService, Depends()],
        user_id: int
):
    return await question_service.question_repository.get_user_questions(
        user_id
    )


@router.put(
    '/{question_id}',
    response_model=schemas.QuestionWithUserOutSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def update_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int,
        question: schemas.QuestionUpdateSchema
):
    return await question_service.update_question(
        question_id, question
    )


@router.delete(
    '/{question_id}',
    status_code=204,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def delete_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int
):
    return await question_service.delete_question(question_id)
