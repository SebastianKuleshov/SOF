from typing import Annotated

from fastapi import Depends

from app.roles.repositories.role import RoleRepository


class RoleService:
    def __init__(
            self,
            role_repository: Annotated[RoleRepository, Depends()]
    ) -> None:
        self.role_repository = role_repository
