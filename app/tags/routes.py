from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.tags.schemas import TagBaseSchema, TagOutSchema, TagUpdateSchema
from app.tags.services import TagService

router = APIRouter(
    prefix='/tags',
    tags=['tags']
)


@router.post(
    '/',
    response_model=TagOutSchema,
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def create_tag(
        tag_service: Annotated[TagService, Depends()],
        tag: TagBaseSchema
):
    return await tag_service.tag_repository.create(tag)


@router.get('/', response_model=list[TagOutSchema])
async def get_tags(
        tag_service: Annotated[TagService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await tag_service.tag_repository.get_multi(skip, limit)


@router.put(
    '/{tag_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def update_tag(
        tag_service: Annotated[TagService, Depends()],
        tag_id: int,
        tag: TagUpdateSchema
):
    return await tag_service.tag_repository.update(tag_id, tag)


@router.delete(
    '/{tag_id}',
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)
async def delete_tag(
        tag_service: Annotated[TagService, Depends()],
        tag_id: int
):
    return await tag_service.tag_repository.delete(tag_id)
