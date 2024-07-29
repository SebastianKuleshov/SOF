from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.comments import schemas as comments_schemas
from app.comments.services import CommentService

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)


@router.post(
    '/',
    response_model=comments_schemas.CommentOutSchema
)
async def create_comment(
        comment_service: Annotated[CommentService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        comment: comments_schemas.CommentCreateSchema
):
    return await comment_service.create_comment(comment, user.id)


@router.get(
    '/',
    response_model=list[comments_schemas.CommentOutSchema]
)
async def get_comments(
        comment_service: Annotated[CommentService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await comment_service.comment_repository.get_multi(
        skip,
        limit
    )


@router.get(
    '/{comment_id}',
    response_model=comments_schemas.CommentOutSchema
)
async def get_comment(
        comment_service: Annotated[CommentService, Depends()],
        comment_id: int
):
    return await comment_service.get_comment(comment_id)


@router.put(
    '/{comment_id}',
    response_model=comments_schemas.CommentOutSchema
)
async def update_comment(
        comment_service: Annotated[CommentService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        comment_id: int,
        comment: comments_schemas.CommentUpdateSchema
):
    return await comment_service.update_comment(
        comment_id,
        user.id,
        comment
    )


@router.delete(
    '/{comment_id}'
)
async def delete_comment(
        comment_service: Annotated[CommentService, Depends()],
        user: Annotated[AuthService.get_user_from_jwt, Depends()],
        comment_id: int
) -> bool:
    return await comment_service.delete_comment(
        comment_id,
        user.id
    )
