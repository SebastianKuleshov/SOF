from fastapi import HTTPException

from app.common.repositories.base_repository import BaseRepository
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    async def check_user_exists(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail='User not found'
            )
        return True
