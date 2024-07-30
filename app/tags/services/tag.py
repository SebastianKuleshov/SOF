from typing import Annotated

from fastapi import Depends, HTTPException

from app.tags.repositories import TagRepository
from app.tags.schemas import TagOutSchema, TagBaseSchema, TagUpdateSchema


class TagService:
    def __init__(
            self,
            tag_repository: Annotated[TagRepository, Depends()]
    ) -> None:
        self.tag_repository = tag_repository

    async def create_tag(
            self,
            tag_schema: TagBaseSchema
    ) -> TagOutSchema:
        tag = await self.tag_repository.get_one({'name': tag_schema.name})
        if tag:
            raise HTTPException(
                status_code=400,
                detail='Tag already exists'
            )
        return await self.tag_repository.create(tag_schema)

    async def update_tag(
            self,
            tag_id: int,
            tag_schema: TagUpdateSchema
    ) -> TagOutSchema:
        await self.tag_repository.get_entity_if_exists(tag_id)
        tag = await self.tag_repository.update(tag_id, tag_schema)
        return TagOutSchema.model_validate(tag)

    async def delete_tag(
            self,
            tag_id: int
    ) -> None:
        await self.tag_repository.get_entity_if_exists(tag_id)
        await self.tag_repository.delete(tag_id)
