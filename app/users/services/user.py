from typing import Annotated

from fastapi import Depends

from app.users.repositories import UserRepository


class UserService:
    def __init__(
            self,
            user_repository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.user_repository = user_repository

    pass
