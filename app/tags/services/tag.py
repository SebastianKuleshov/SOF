from typing import Annotated

from fastapi import Depends

from app.tags.repositories import TagRepository


class TagService:
    def __init__(
            self,
            tag_repository: Annotated[TagRepository, Depends()]
    ) -> None:
        self.tag_repository = tag_repository
