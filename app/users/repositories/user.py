from sqlalchemy import select

from app.common.repositories.base_repository import BaseRepository
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    async def update_reputation(self, user_id: int, is_upvote: bool) -> None:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if is_upvote else -1
        await self.session.commit()

    async def get_by_email(self, email: str) -> UserModel:
        stmt = select(self.model).where(email == self.model.email)
        return await self.session.scalar(stmt)
