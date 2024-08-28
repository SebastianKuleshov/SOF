from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.comments import schemas as comments_schemas
from app.comments.services import CommentService

router = APIRouter(
    prefix='/comments',
    tags=['comments'],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)


@router.post(
    '/',
    response_model=comments_schemas.CommentOutSchema,
    dependencies=[Depends(AuthService.require_permissions(
        {'create_own_comment'}))]
)
async def create_comment(
        comment_service: Annotated[CommentService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        comment: comments_schemas.CommentCreateSchema
):
    return await comment_service.create_comment(
        comment,
        user_id
    )


@router.put(
    '/{comment_id}',
    response_model=comments_schemas.CommentOutSchema,
    dependencies=[Depends(AuthService.require_permissions({'update_own_comment'}))]
)
async def update_comment(
        comment_service: Annotated[CommentService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        comment_id: int,
        comment: comments_schemas.CommentUpdateSchema
):
    return await comment_service.update_comment(
        comment_id,
        user_id,
        comment
    )


@router.delete(
    '/{comment_id}',
    dependencies=[Depends(AuthService.require_permissions(
        {'delete_own_comment'}))]
)
async def delete_comment(
        comment_service: Annotated[CommentService, Depends()],
        user_id: Annotated[AuthService.get_user_id_from_request, Depends()],
        comment_id: int
) -> bool:
    return await comment_service.delete_comment(
        comment_id,
        user_id
    )
