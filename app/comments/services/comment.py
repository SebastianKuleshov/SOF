from typing import Annotated

from fastapi import Depends

from app.comments.repositories import CommentRepository


class CommentService:
    def __init__(
            self,
            comment_repository: Annotated[CommentRepository, Depends()]
    ) -> None:
        self.comment_repository = comment_repository

    pass
