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
