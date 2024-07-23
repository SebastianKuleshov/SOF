from pydantic import EmailStr

from app.common.repositories.base_repository import BaseRepository
from app.dependencies import verify_password
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    async def authenticate_user(
            self,
            email: EmailStr,
            password: str
    ) -> UserModel | None:
        user = await self.get_one({'email': email})
        if not user:
            return None
        if not await verify_password(password, user.password):
            return None
        return user
