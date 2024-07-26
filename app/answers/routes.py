from typing import Annotated

from fastapi import APIRouter, Depends

from app.answers import schemas as answer_schemas
from app.answers.services import AnswerService
from app.auth.services import AuthService

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


@router.put(
    '/{answer_id}',
    response_model=answer_schemas.AnswerWithUserOutSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def update_answer(
        answer_service: Annotated[AnswerService, Depends()],
        answer_id: int,
        answer: answer_schemas.AnswerUpdateSchema
):
    return await answer_service.update_answer(answer_id, answer)


@router.delete(
    '/{answer_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def delete_answer(
        answer_service: Annotated[AnswerService, Depends()],
        answer_id: int
) -> bool:
    return await answer_service.delete_answer(answer_id)
