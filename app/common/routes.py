from typing import Annotated

from fastapi import APIRouter, Depends

from app.questions import schemas as question_schemas
from app.questions.services import QuestionService

router = APIRouter(
    prefix='/search',
    tags=['search']
)


@router.get(
    '',
    response_model=list[question_schemas.QuestionForListOutSchema]
)
async def search(
        question_service: Annotated[QuestionService, Depends()],
        query: str
):
    return await question_service.search(query)
