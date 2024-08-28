from typing import Annotated

from fastapi import Depends, HTTPException

from app.tags.repositories import TagRepository
from app.tags.schemas import TagBaseSchema, TagOutSchema


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
        tag_model = await self.tag_repository.get_one(
            {'name': tag_schema.name}
        )
        if tag_model:
            raise HTTPException(
                status_code=400,
                detail='Tag already exists'
            )
        tag_model = await self.tag_repository.create(tag_schema)
        return TagOutSchema.model_validate(tag_model)
