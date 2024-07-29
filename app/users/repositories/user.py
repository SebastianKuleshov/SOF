from fastapi import HTTPException

from app.common.repositories.base_repository import BaseRepository
from app.users.models import UserModel
from app.users.schemas import UserOutSchema


class UserRepository(BaseRepository):
    model = UserModel

    async def get_user_if_exists(
            self,
            user_id: int
    ) -> UserOutSchema | None:
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail='User not found'
            )
        return UserOutSchema.model_validate(user)
