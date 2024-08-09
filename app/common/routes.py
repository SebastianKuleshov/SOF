from typing import Annotated

from fastapi import APIRouter, Depends

from app.common.services import SearchService
from app.questions import schemas as question_schemas

router = APIRouter(
    prefix='/search',
    tags=['search']
)


@router.get(
    '',
    response_model=list[question_schemas.QuestionForListOutSchema]
)
async def search(
        search_service: Annotated[SearchService, Depends()],
        query: str
):
    return await search_service.search(query)
