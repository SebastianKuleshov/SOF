from typing import Annotated

from fastapi import Depends, HTTPException

from app.answers.repositories import AnswerRepository
from app.comments.repositories import CommentRepository
from app.comments.schemas import CommentCreateSchema, CommentOutSchema, \
    CommentCreatePayloadSchema, CommentUpdateSchema
from app.questions.repositories import QuestionRepository
from app.users.services import UserService


class CommentService:
    def __init__(
            self,
            comment_repository: Annotated[CommentRepository, Depends()],
            question_repository: Annotated[QuestionRepository, Depends()],
            answer_repository: Annotated[AnswerRepository, Depends()],
            user_service: Annotated[UserService, Depends()]
    ) -> None:
        self.comment_repository = comment_repository
        self.question_repository = question_repository
        self.answer_repository = answer_repository
        self.user_service = user_service

    async def create_comment(
            self,
            comment_schema: CommentCreateSchema,
            user_id: int
    ) -> CommentOutSchema:
        comment_schema = CommentCreatePayloadSchema(
            **comment_schema.model_dump(),
            user_id=user_id
        )
        if comment_schema.question_id:
            await self.question_repository.get_entity_if_exists(
                comment_schema.question_id
            )
        if comment_schema.answer_id:
            await self.answer_repository.get_entity_if_exists(
                comment_schema.answer_id
            )
        return await self.comment_repository.create(comment_schema)

    async def get_comment(self, comment_id: int) -> CommentOutSchema:
        comment = await self.comment_repository.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail='Comment not found'
            )
        return comment

    async def update_comment(
            self,
            comment_id: int,
            user_id: int,
            comment_schema: CommentUpdateSchema
    ) -> CommentOutSchema:
        comment = await self.comment_repository.get_entity_if_exists(
            comment_id
        )
        user_permissions = await self.user_service.get_user_permissions(user_id)
        if comment.user_id != user_id and 'update_any_comment' not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to update this comment'
            )
        await self.comment_repository.update(comment_id, comment_schema)
        return await self.comment_repository.get_by_id(comment_id)

    async def delete_comment(
            self,
            comment_id: int,
            user_id: int
    ) -> bool:
        comment = await self.comment_repository.get_entity_if_exists(
            comment_id
        )
        user_permissions = await self.user_service.get_user_permissions(user_id)
        if comment.user_id != user_id and 'delete_any_comment' not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail='You are not allowed to delete this comment'
            )
        return await self.comment_repository.delete(comment_id)
