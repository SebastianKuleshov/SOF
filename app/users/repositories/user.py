from app.common.repositories.base_repository import BaseRepository
from app.users.models import UserModel


class UserRepository(BaseRepository):
    model = UserModel

    async def update_reputation(self, user_id: int, reputation: bool) -> None:
        user = await self.get_by_id(user_id)
        user.reputation += 1 if reputation else -1
        await self.session.commit()
