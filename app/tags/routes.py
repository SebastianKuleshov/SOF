from typing import Annotated

from fastapi import APIRouter, Depends

from app.tags import schemas as tag_schemas
from app.tags.services import TagService

router = APIRouter(
    prefix='/tags',
    tags=['tags']
)


@router.get('/', response_model=list[tag_schemas.TagOutSchema])
async def get_tags(
        tag_service: Annotated[TagService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await tag_service.tag_repository.get_multi(skip, limit)


@router.get(
    '/{tag_id}',
    response_model=tag_schemas.TagOutSchema
)
async def get_tag(
        tag_service: Annotated[TagService, Depends()],
        tag_id: int
):
    return await tag_service.tag_repository.get_entity_if_exists(tag_id)
