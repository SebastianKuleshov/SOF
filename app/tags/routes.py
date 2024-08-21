from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth.services import AuthService
from app.tags import schemas as tag_schemas
from app.tags.services import TagService

public_router = APIRouter(
    prefix='/tags',
    tags=['tags']
)

private_router = APIRouter(
    prefix='/tags',
    tags=['tags'],
    dependencies=[Depends(AuthService.get_user_from_jwt)]
)


@public_router.get('/', response_model=list[tag_schemas.TagOutSchema])
async def get_tags(
        tag_service: Annotated[TagService, Depends()],
        skip: int = 0,
        limit: int = 100
):
    return await tag_service.tag_repository.get_multi(skip, limit)


@public_router.get(
    '/{tag_id}',
    response_model=tag_schemas.TagOutSchema
)
async def get_tag(
        tag_service: Annotated[TagService, Depends()],
        tag_id: int
):
    return await tag_service.tag_repository.get_entity_if_exists(tag_id)


@private_router.post(
    '/',
    response_model=tag_schemas.TagOutSchema,
    dependencies=[Depends(AuthService.PermissionChecker(['create_tag']))]
)
async def create_tag(
        tag_service: Annotated[TagService, Depends()],
        tag: tag_schemas.TagBaseSchema
):
    return await tag_service.create_tag(tag)


@private_router.delete(
    '/{tag_id}',
    dependencies=[Depends(AuthService.PermissionChecker(['delete_tag']))]
)
async def delete_tag(
        tag_service: Annotated[TagService, Depends()],
        tag_id: int
) -> bool:
    return await tag_service.tag_repository.delete(tag_id)
