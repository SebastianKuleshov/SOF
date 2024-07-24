from typing import Annotated

from fastapi import APIRouter, Depends

from app.questions import schemas
from app.questions.services import QuestionService

router = APIRouter(
    prefix='/questions',
    tags=['questions']
)


@router.post('/', response_model=schemas.QuestionOutSchema)
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
    return await question_service.question_repository.get_question_by_id(
        question_id
    )


@router.put(
    '/{question_id}',
    response_model=schemas.QuestionWithUserOutSchema
)
async def update_question(
        question_service: Annotated[QuestionService, Depends()],
        question_id: int,
        question: schemas.QuestionUpdateSchema
):
    return await question_service.update(
        question_id, question
    )
